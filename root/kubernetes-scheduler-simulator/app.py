import streamlit as st
import subprocess
from pathlib import Path
import shutil

# ============================
# ✅ Lists
# ============================
DATA_ROOT = Path("data")

def ensure_base_pod_lists():
    base_dirs = [p for p in DATA_ROOT.glob("openb_pod_list_*") if p.is_dir()]
    if not base_dirs:
        subprocess.run(["bash", "prepare_input.sh"], check=True, cwd=DATA_ROOT)
        base_dirs = [p for p in DATA_ROOT.glob("openb_pod_list_*") if p.is_dir()]
    return sorted(p.name for p in base_dirs)

BASE_POD_LISTS = ensure_base_pod_lists()

POLICIES = [
    "Random",
    "DotProd",
    "GpuClustering",
    "GpuPacking",
    "BestFit",
    "FGD",
    "RlSched",
]

GPU_MODES = ["<none>", "random", "best", "FGD"]
DIMEXT_MODES = ["<none>", "merge", "share"]
NORM_MODES = ["<none>", "max"]

DEFAULT_RACKS = 10
DEFAULT_SKEW = 1

main_col, cmd_col = st.columns([2, 1])

with main_col:
    base_col, topo_col = st.columns(2)

    with base_col:
        st.subheader("Create Topology Aware Configuration From:")
        src_base = st.selectbox("", BASE_POD_LISTS, key="src_base_select")

    with topo_col:
        st.subheader("Topology Options")
        enable_topology = st.radio("Enable Rack & Skew Customization?", ["No", "Yes"], index=0)

        if enable_topology == "Yes":
            rack_mod = st.slider("Number of Racks", 1, 50, DEFAULT_RACKS)
            max_skew = st.slider("Skew Value", 1, 10, DEFAULT_SKEW)
        else:
            st.write("**Number of Racks:**")
            st.progress(0)
            st.caption("(disabled)")
            st.write("**Skew Value:**")
            st.progress(0)
            st.caption("(disabled)")
            rack_mod = DEFAULT_RACKS
            max_skew = DEFAULT_SKEW

        if st.button("Process Topology (Add Racks & Constraints)"):
            src_dir = DATA_ROOT / src_base
            out_dir = DATA_ROOT / f"{src_base}_topology_configuration"
            out_dir.mkdir(exist_ok=True)

            cmd = [
                "python3", "process_openb_dir.py",
                str(src_dir),
                "--rack-mod", str(rack_mod),
                "--max-skew", str(max_skew)
            ]
            st.write("### Running Topology Processor:")
            st.code(" ".join(cmd))
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.stdout:
                st.code(result.stdout)
            if result.stderr:
                st.error(result.stderr)

            for yaml_file in src_dir.glob("*.yaml"):
                shutil.copy2(yaml_file, out_dir / yaml_file.name)

            st.session_state["selected_input"] = str(out_dir)

    # --- Sync selection when base changes ---
    prev_src_base = st.session_state.get("prev_src_base")
    if prev_src_base != src_base:
        st.session_state["selected_input"] = str(DATA_ROOT / src_base)
        st.session_state["prev_src_base"] = src_base

    st.title("Kubernetes Scheduler Simulator Runner")

    input_dir_path = Path(st.session_state.get("selected_input", DATA_ROOT / src_base))
    input_dir_choice = input_dir_path.name
    st.markdown(f"**Using Input Directory:** `{input_dir_choice}`")

    policy = st.selectbox("Select Scheduling Policy", POLICIES)
    gpu_sel = st.selectbox("GPU Selection", GPU_MODES)
    dimext = st.selectbox("Dimension Extension", DIMEXT_MODES)
    norm = st.selectbox("Normalization", NORM_MODES)

    rl_endpoint = ""
    rl_timeout = 0
    if policy == "RlSched":
        rl_endpoint = st.text_input("RlScheduler endpoint", key="rl_endpoint")
        rl_timeout = st.number_input("RlScheduler timeout (ms)", min_value=0, value=0, step=1, key="rl_timeout")

    expdir = f"experiments/2023_0511/{input_dir_choice}/{policy}/1.3/42"

    args_lines = [
        f'-d "{expdir}"',
        "-e",
        "-b",
        f'-f data/{input_dir_choice}',
        f'-{policy} 1000',
    ]
    if gpu_sel != "<none>":
        args_lines.append(f"-gpusel {gpu_sel}")
    if dimext != "<none>":
        args_lines.append(f"-dimext {dimext}")
    if norm != "<none>":
        args_lines.append(f"-norm {norm}")
    if policy == "RlSched":
        if rl_endpoint:
            args_lines.append(f"--rl-endpoint {rl_endpoint}")
        if rl_timeout:
            args_lines.append(f"--rl-timeout-ms {int(rl_timeout)}")
    args_lines += [
        "-tune 1.3",
        "-tuneseed 42",
        "--shuffle-pod=true",
        f'-z "{expdir}/snapshot/ds01"',
    ]

    cli_multiline = "python3 scripts/generate_config_and_run.py \\\n  " + " \\\n  ".join(args_lines)
    analysis_multiline = "python3 scripts/analysis.py \\\n  -f \\\n  -g " + expdir
    full_cmd_multiline = (
        f'mkdir -p "{expdir}" && touch "{expdir}/terminal.out" && \\\n'
        f"{cli_multiline} | tee -a \"{expdir}/terminal.out\" && \\\n"
        f"{analysis_multiline} | tee -a \"{expdir}/terminal.out\""
    )

    if st.button("Run Simulation"):
        result = subprocess.run(full_cmd_multiline, shell=True, capture_output=True, text=True)
        if result.stdout:
            st.code(result.stdout)
        if result.stderr:
            st.error(result.stderr)
        st.success("Simulation completed successfully!")

with cmd_col:
    if "preview_height" not in st.session_state:
        st.session_state.preview_height = 180

    with st.expander("Preview settings"):
        st.session_state.preview_height = st.number_input(
            "Preview height (px)",
            min_value=120,
            max_value=1200,
            value=st.session_state.preview_height,
            step=20,
        )

    st.markdown(
        f"""
        <style>
          /* colour comes from st.code; we modify layout only */
          div[data-testid="stCodeBlock"] pre {{
            white-space: pre-wrap !important;      /* wrap nicely */
            word-break: break-word !important;     /* break long tokens */
          }}
          div[data-testid="stCodeBlock"] {{
            height: {st.session_state.preview_height}px !important;  /* stable height across reruns */
            overflow: auto !important;            /* scroll if needed */
            resize: both !important;              /* mouse-resize */
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Generated Command (Copy Only)")
    st.code(full_cmd_multiline, language="bash")
