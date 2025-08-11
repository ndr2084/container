package plugin

import (
	"bytes"
	"context"
	"encoding/json"
	"math"
	"net/http"
	"time"

	corev1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/kubernetes/pkg/scheduler/framework"
	frameworkruntime "k8s.io/kubernetes/pkg/scheduler/framework/runtime"

	simontype "github.com/hkust-adsl/kubernetes-scheduler-simulator/pkg/type"
	gpushareutils "github.com/hkust-adsl/kubernetes-scheduler-simulator/pkg/type/open-gpu-share/utils"
	"github.com/hkust-adsl/kubernetes-scheduler-simulator/pkg/utils"
)

// RLSchedulerScoreArgs defines optional configuration for the RlSchedulerScore plugin.
type RLSchedulerScoreArgs struct {
	// CpuWeight determines the weight of the remaining CPU when computing the score.
	// GpuWeight is applied to the remaining GPU ratio.
	// If the sum is zero, both default to 0.5.
	CpuWeight  float64 `json:"cpuWeight,omitempty"`
	GpuWeight  float64 `json:"gpuWeight,omitempty"`
	RlEndpoint string  `json:"rlEndpoint,omitempty"`
	RlTimeout  int64   `json:"rlTimeoutMs,omitempty"`
}

// RLSchedulerScorePlugin gives each node a score based on free CPU and GPU resources.
type RLSchedulerScorePlugin struct {
	handle framework.Handle
	args   *RLSchedulerScoreArgs
}

type rlRequest struct {
	PodName  string  `json:"pod"`
	NodeName string  `json:"node"`
	CpuRatio float64 `json:"cpu_ratio"`
	GpuRatio float64 `json:"gpu_ratio"`
}

type rlResponse struct {
	Score float64 `json:"score"`
}

var _ framework.ScorePlugin = &RLSchedulerScorePlugin{}

// NewRLSchedulerScorePlugin creates a new plugin instance from runtime configuration.
func NewRLSchedulerScorePlugin(configuration runtime.Object, handle framework.Handle) (framework.Plugin, error) {
	args := &RLSchedulerScoreArgs{CpuWeight: 0.5, GpuWeight: 0.5}
	if configuration != nil {
		if err := frameworkruntime.DecodeInto(configuration, args); err != nil {
			return nil, err
		}
	}
	sum := args.CpuWeight + args.GpuWeight
	if sum <= 0 {
		args.CpuWeight, args.GpuWeight = 0.5, 0.5
	} else {
		args.CpuWeight = args.CpuWeight / sum
		args.GpuWeight = args.GpuWeight / sum
	}
	return &RLSchedulerScorePlugin{handle: handle, args: args}, nil
}

// Name returns the plugin name.
func (plugin *RLSchedulerScorePlugin) Name() string {
	return simontype.RLSchedulerScorePluginName
}

// Score calculates score based on remaining CPU and GPU capacity.
// Scores are normalised to [0,100].
func (plugin *RLSchedulerScorePlugin) Score(ctx context.Context, state *framework.CycleState, pod *corev1.Pod, nodeName string) (int64, *framework.Status) {
	nodeResPtr := utils.GetNodeResourceViaHandleAndName(plugin.handle, nodeName)
	if nodeResPtr == nil {
		return framework.MinNodeScore, framework.NewStatus(framework.Success)
	}
	nodeRes := *nodeResPtr
	podRes := utils.GetPodResource(pod)
	if !utils.IsNodeAccessibleToPod(nodeRes, podRes) {
		return framework.MinNodeScore, framework.NewStatus(framework.Success)
	}

	cpuRatio := 0.0
	if nodeRes.MilliCpuCapacity > 0 {
		cpuRatio = float64(nodeRes.MilliCpuLeft-podRes.MilliCpu) / float64(nodeRes.MilliCpuCapacity)
	}
	cpuRatio = math.Max(0, math.Min(1, cpuRatio))

	gpuRatio := 1.0
	if podRes.GpuNumber > 0 || nodeRes.GpuNumber > 0 {
		totalGpu := nodeRes.GpuNumber * gpushareutils.MILLI
		if totalGpu > 0 {
			gpuRatio = float64(nodeRes.GetTotalMilliGpuLeft()-podRes.TotalMilliGpu()) / float64(totalGpu)
		} else {
			gpuRatio = 0
		}
		gpuRatio = math.Max(0, math.Min(1, gpuRatio))
	}

	if plugin.args.RlEndpoint != "" {
		req := rlRequest{PodName: pod.GetName(), NodeName: nodeName, CpuRatio: cpuRatio, GpuRatio: gpuRatio}
		body, err := json.Marshal(req)
		if err == nil {
			timeout := time.Duration(plugin.args.RlTimeout) * time.Millisecond
			client := &http.Client{}
			if timeout > 0 {
				client.Timeout = timeout
			}
			httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, plugin.args.RlEndpoint, bytes.NewReader(body))
			if err == nil {
				httpReq.Header.Set("Content-Type", "application/json")
				resp, err := client.Do(httpReq)
				if err == nil {
					defer resp.Body.Close()
					var rResp rlResponse
					if err := json.NewDecoder(resp.Body).Decode(&rResp); err == nil {
						rlScore := math.Max(0, math.Min(1, rResp.Score))
						return int64(rlScore * float64(framework.MaxNodeScore)), framework.NewStatus(framework.Success)
					}
				}
			}
		}
	}

	score := cpuRatio*plugin.args.CpuWeight + gpuRatio*plugin.args.GpuWeight
	score = math.Max(0, math.Min(1, score))
	return int64(score * float64(framework.MaxNodeScore)), framework.NewStatus(framework.Success)
}

// ScoreExtensions returns nil as no extensions are used.
func (plugin *RLSchedulerScorePlugin) ScoreExtensions() framework.ScoreExtensions {
	return nil
}
