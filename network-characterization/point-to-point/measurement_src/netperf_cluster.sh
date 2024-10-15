#!/usr/bin/bash

# nodes/hosts differentiation is a workaround for pending DNS/hosts entries
NODES=(10.97.4.1 10.97.4.2 10.97.4.3 10.97.4.4 10.97.3.1 10.97.3.2)
HOSTS=(cn01 cn02 cn03 cn04 infra1 infra2)

NETPERF="/tmp/pfriese/bin/netperf"
NETSERVER="/tmp/pfriese/bin/netserver"

NETPERF_SERVER_ARGS=
NETPERF_CLIENT_ARGS="-t TCP_RR -l 60 -- -o min_latency,mean_latency,max_latency,stddev_latency"

TIMEOUT="timeout -k 180 120" # Note: make sure timeout values (-k for KILL, last for normal) are large enough for iperf3 to finish!

OUTDIR="$(pwd)/measurements_netperf_$(date +%y-%m-%dT%H%M)"
OUTFILE_STEM="$OUTDIR/measurements_netperf_$(date +%y-%m-%dT%H%M)"

OUTFILE="$OUTFILE_STEM.csv"
OUTFILE_META="$OUTFILE_STEM"_"meta.md"

function bits_to_gbits {
	echo $(python3 -c "print(f'{$1 / 1e9:.12f}')")
}

mkdir -p $OUTDIR
echo "server;client;min_latency;mean_latency;max_latency;stddev_latency" >> $OUTFILE

read -d '' meta_info << EOF
Measurement Start Timestamp: \`$(date +%c) ($(date +%s))\`
Server Arguments: \`$NETPERF_SERVER_ARGS\`
Client Arguments: \`$NETPERF_CLIENT_ARGS\`
Measurement tool: \`$NETPERF\` (Version: \`$(ssh cn01 $NETPERF -V)\`)
EOF

echo "$meta_info" > "$OUTFILE_META"

for server_node_idx in "${!NODES[@]}"
do
	ssh -f "${HOSTS[$server_node_idx]}" "$TIMEOUT" "$NETSERVER $NETPERF_SERVER_ARGS" >/dev/null 2>&1
	sleep 1s
	for client_node_idx in "${!NODES[@]}"
	do
		if [[ "$server_node_idx" == "$client_node_idx" ]]; then continue
		fi
		printf "${HOSTS[$server_node_idx]} -> ${HOSTS[$client_node_idx]}"

		client=$(ssh "${HOSTS[$client_node_idx]}" "$TIMEOUT" "$NETPERF -H ${NODES[$server_node_idx]} $NETPERF_CLIENT_ARGS")
		printf "$client" >> "$OUTFILE_STEM"_"${HOSTS[$server_node_idx]}"_"${HOSTS[$client_node_idx]}.txt"

		latency=$(printf "$client"|tail -n 1|sed 's/,/;/g') # floats and comma as separator doesn't match - fix netperf output

		echo "${HOSTS[$server_node_idx]};${HOSTS[$client_node_idx]};$latency" >> "$OUTFILE"
		echo ": $latency"
	done
	ssh -f "${HOSTS[$server_node_idx]}" "$TIMEOUT" "pkill netserver" # netserver doesn't have an "exit after test" option, so do it manually

	echo ""
done