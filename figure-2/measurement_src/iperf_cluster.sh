#!/usr/bin/bash

# nodes/hosts differentiation is a workaround for pending DNS/hosts entries
NODES=(10.97.4.1 10.97.4.2 10.97.4.3 10.97.4.4 10.97.3.1 10.97.3.2)
HOSTS=(cn01 cn02 cn03 cn04 infra1 infra2)

IPERF="/tmp/pfriese/bin/iperf3"

IPERF_SERVER_ARGS=
IPERF_CLIENT_ARGS="--parallel 8 --time 60 --omit 10 --json --zerocopy"

TIMEOUT="timeout -k 120 90" # Note: make sure timeout values (-k for KILL, last for normal) are large enough for iperf3 to finish!

OUTDIR="$(pwd)/measurements_iperf_$(date +%y-%m-%dT%H%M)"
OUTFILE_STEM="$OUTDIR/measurements_iperf_$(date +%y-%m-%dT%H%M)"

OUTFILE="$OUTFILE_STEM.csv"
OUTFILE_META="$OUTFILE_STEM"_"meta.md"

function bits_to_gbits {
	echo $(python3 -c "print(f'{$1 / 1e9:.12f}')")
}

mkdir -p $OUTDIR
echo "from;to;throughput_gbitsec" >> $OUTFILE

read -d '' meta_info << EOF
Measurement Start Timestamp: \`$(date +%c) ($(date +%s))\`
Server Arguments: \`$IPERF_SERVER_ARGS\`
Client Arguments: \`$IPERF_CLIENT_ARGS\`
Measurement tool: \`$IPERF\` (Version: \`$(ssh cn01 $IPERF --version)\`)
EOF

echo "$meta_info" > "$OUTFILE_META"

for server_node_idx in "${!NODES[@]}"
do
	for client_node_idx in "${!NODES[@]}"
	do
		if [[ "$server_node_idx" == "$client_node_idx" ]]; then
			continue
		fi
		echo "${HOSTS[$server_node_idx]} -> ${HOSTS[$client_node_idx]}"
		
		ssh -f "${HOSTS[$server_node_idx]}" "$TIMEOUT" "$IPERF -s -1 $IPERF_SERVER_ARGS" >/dev/null 2>&1
		sleep 1s
		
		client=$(ssh "${HOSTS[$client_node_idx]}" "$TIMEOUT" "$IPERF -c ${NODES[$server_node_idx]} $IPERF_CLIENT_ARGS")
		
		client_sent=$(printf "$client"|jq '.end.sum_sent.bits_per_second')
		client_received=$(printf "$client"|jq '.end.sum_received.bits_per_second')

		printf "$client" >> "$OUTFILE_STEM"_"${HOSTS[$server_node_idx]}"_"${HOSTS[$client_node_idx]}.json"
		echo "${HOSTS[$server_node_idx]};${HOSTS[$client_node_idx]};$(bits_to_gbits "$client_sent")" >> $OUTFILE
		echo "${HOSTS[$server_node_idx]};${HOSTS[$client_node_idx]};$(bits_to_gbits "$client_received")" >> $OUTFILE
	done
	echo ""
done