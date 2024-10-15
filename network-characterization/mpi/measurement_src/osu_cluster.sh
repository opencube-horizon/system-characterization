#!/usr/bin/bash

# option parsing code adapted from Robert Siemer, https://stackoverflow.com/a/29754866, CC BY-SA 4.0
! getopt --test > /dev/null 
if [[ ${PIPESTATUS[0]} -ne 4 ]]; then
    exit 1
fi

LONGOPTS=mpi-type:,host-set:
OPTIONS=
! PARSED=$(getopt --options=$OPTIONS --longoptions=$LONGOPTS --name "$0" -- "$@")
if [[ ${PIPESTATUS[0]} -ne 0 ]]; then
    exit 1
fi

MPI_TYPE="mpich"

# nodes/hosts differentiation is a workaround for pending DNS/hosts entries
NODES=(10.97.4.1 10.97.4.2 10.97.4.3 10.97.4.4)
HOSTS=(cn01 cn02 cn03 cn04)
HOSTSET="cn"
MPI_ARGS=""

eval set -- "$PARSED"
while true; do
    case "$1" in
      --mpi-type)
        MPI_TYPE="$2"
  			shift 2
    		;;
      --host-set)
        HOSTSET="$2"
        if [[ "$HOSTSET" == "cn" ]]; then
					NODES=(10.97.4.1 10.97.4.2 10.97.4.3 10.97.4.4)
					HOSTS=(cn01 cn02 cn03 cn04)
				elif [[ "$HOSTSET" == "infra" ]]; then
					NODES=(10.97.3.1 10.97.3.2)
					HOSTS=(infra1 infra2)
				else echo "Invalid host-set!"
				fi
        shift 2
        ;;
      --)
        shift
        break
        ;;	
      *)
				echo "$@"
	      echo "Programming error"
	      exit 3
	      ;;
    esac
done

case "$HOSTSET" in 
 "cn")
		case "$MPI_TYPE" in
			"openmpi")
				MPIRUN="/home/f5b3a7ad-ecee-426f-b7b7-1c62c2706216/build/spack/opt/spack/linux-opensuse15-neoverse_n1/gcc-7.5.0/openmpi-4.1.6-jwwrsiru34dllaww7plas5bmt6ae2n4u/bin/mpirun"
				OSU_BASEPATH="/home/pfriese/build/osu-openmpi416-ucx/c/mpi"
				;;
		esac
		;;
 "infra")
	case "$MPI_TYPE" in
		"openmpi")
			MPIRUN="/home/f5b3a7ad-ecee-426f-b7b7-1c62c2706216/build/spack_infra/opt/spack/linux-opensuse15-zen/gcc-7.5.0/openmpi-4.1.6-efmvxxr6sninfblcgndhcyobpmsnpj3w/bin/mpirun"
			OSU_BASEPATH="/home/pfriese/build_infra/osu-openmpi/c/mpi"
			MPI_ARGS="--mca btl_tcp_if_include eth0"
			;;
		"openmpi-native")
			MPIRUN="/opt/openmpi-4.1.5/bin/mpirun"
			OSU_BASEPATH="/home/pfriese/build_infra/osu-openmpi-native/c/mpi"
			;;
	esac
	;;
esac


OSU_TESTS_PT2PT=(pt2pt/standard/osu_bw
				 			   pt2pt/standard/osu_bibw 
				 				 pt2pt/standard/osu_latency)
OSU_TESTS_COLLECTIVES=(
					     collective/blocking/osu_gather
				       collective/blocking/osu_allgather
					     collective/blocking/osu_reduce
				       collective/blocking/osu_allreduce
				       collective/blocking/osu_alltoall
				       collective/blocking/osu_bcast
				       )


OSU_GLOBAL_ARGS="--tail-lat --message-size :4194304"
FILE_STEM="measurements_osu_$MPI_TYPE"_"$HOSTSET"_"$(date +%y-%m-%dT%H%M)"
OUTDIR="$(pwd)/$FILE_STEM"

OUTFILE_META="$OUTDIR/$FILE_STEM""_meta.md"

mkdir -p $OUTDIR

read -d '' meta_info << EOF
Measurement Start Timestamp: \`$(date +%c) ($(date +%s))\`
mpirun: \`$MPIRUN\`
Nodes: \`${NODES[@]}\`
Measurement tool: \`$MPIRUN\` (Version: \`$($MPIRUN --version 2>/dev/null)\`)
OSU version: \`$(ssh ${NODES[1]} "$OSU_BASEPATH/pt2pt/standard/osu_bw --version")\`
EOF

echo "$meta_info" > "$OUTFILE_META"

echo ""
echo "Point-to-Point tests"

for test_idx in "${!OSU_TESTS_PT2PT[@]}"
do
	test=${OSU_TESTS_PT2PT[test_idx]}
	test_fn=$(basename $test) 
	printf "\r[$(($test_idx+1))/${#OSU_TESTS_PT2PT[@]}] Running %-50s" "$test"

	CMD="$MPIRUN $MPI_ARGS --host ${NODES[0]},${NODES[1]} $OSU_BASEPATH/$test $OSU_GLOBAL_ARGS"
	client=$(ssh "${NODES[0]}" "$CMD" 2>/dev/null)
	echo "$client" >> "$OUTDIR/$FILE_STEM""_$test_fn.dat"
done
echo ""


echo ""
echo "Collective tests"

HOST_ALL=$(echo "${NODES[@]}" | tr ' ' ',')
for test_idx in "${!OSU_TESTS_COLLECTIVES[@]}"
do
	test=${OSU_TESTS_COLLECTIVES[test_idx]}
	test_fn=$(basename $test)
	printf "\r[$(($test_idx+1))/${#OSU_TESTS_COLLECTIVES[@]}] Running %-50s" "$test"
	CMD="$MPIRUN $MPI_ARGS --host $HOST_ALL $OSU_BASEPATH/$test $OSU_GLOBAL_ARGS"
	client=$(ssh "${NODES[0]}" "$CMD" 2>/dev/null)
	echo "$client" >> "$OUTDIR/$FILE_STEM""_$test_fn.dat"
done
echo ""