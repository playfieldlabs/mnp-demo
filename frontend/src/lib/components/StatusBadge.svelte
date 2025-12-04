<script lang="ts">
	import { Status } from '$gen/agent_platform/common/v1/types_pb.js';
	import { getStatusColor, getStatusLabel } from '$utils/format';

	export let status: Status = Status.UNSPECIFIED;
	export let compact = false;

	$: label = getStatusLabel(status);
	$: color = getStatusColor(status);
</script>

<span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-sm bg-surface-2 font-medium uppercase tracking-wider {compact ? 'text-xs py-0.5 px-1.5' : 'text-xs'}" style={`color: ${color}`}>
	{label}
</span>

