#!/usr/bin/bash

# nodes/hosts differentiation is a workaround for pending DNS/hosts entries
NODES=(10.97.3.1 10.97.3.2)
NODES_SL=(10.115.3.1 10.115.3.2)
HOSTS=(infra1 infra2)

CXI_BASEPATH='/opt/libcxi/bin'

CXI_TESTS=(cxi_read_bw cxi_write_bw cxi_send_bw
	       cxi_read_lat cxi_write_lat cxi_send_lat)

CXI_SERVER_ARGS=
CXI_CLIENT_ARGS="--size=1:4194304"

OUTDIR="$(pwd)/measurements_$(date +%y-%m-%dT%H%M)"
OUTFILE_STEM="$OUTDIR/measurements_$(date +%y-%m-%dT%H%M)"

function bits_to_gbits {
	echo $(python3 -c "print(f'{$1 / 1e9:.12f}')")
}

mkdir -p $OUTDIR

read -d '' meta_info << EOF
Measurement Start Timestamp: \`$(date +%c) ($(date +%s))\`
Server Arguments: \`$CXI_SERVER_ARGS\`
Client Arguments: \`$CXI_CLIENT_ARGS\`
Nodes: $(printf '%s,' "${NODES[@]}")
Measurement tools: $(printf '%s,' "${CXI_TESTS[@]}") (Version: \`$(ssh ${NODES[0]} $CXI_BASEPATH/${CXI_TESTS[0]} --version)\`)
EOF

echo "$meta_info" > "$OUTFILE_STEM"_"meta.md"

server_node_idx=0
client_node_idx=1

for test_idx in "${!CXI_TESTS[@]} "
do 
	printf "\r[$(($test_idx+1))/${#CXI_TESTS[@]}] %-50s" ${CXI_TESTS[$test_idx]}
	executable="$CXI_BASEPATH/${CXI_TESTS[$test_idx]}"

	ssh -f "${NODES[$server_node_idx]}" "taskset -c 4" "timeout 180" "$executable $CXI_SERVER_ARGS" >/dev/null 2>&1

	ssh "${NODES[$client_node_idx]}" "taskset -c 4" "timeout 180" "$executable $CXI_CLIENT_ARGS ${NODES_SL[$server_node_idx]}" >> "$OUTFILE_STEM"_"${CXI_TESTS[$test_idx]}.dat"
done
