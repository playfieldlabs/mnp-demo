import { Status } from '$gen/agent_platform/common/v1/types_pb.js';

export function formatDateTime(value?: string | number | Date | { seconds?: bigint | number; nanos?: number }) {
	if (!value) return '—';
	let date: Date;
	if (typeof value === 'object' && value !== null && 'seconds' in value && !(value instanceof Date)) {
		date = new Date(Number(value.seconds) * 1000);
	} else if (typeof value === 'string' || typeof value === 'number') {
		date = new Date(value);
	} else {
		date = value as Date;
	}
	return date.toLocaleString(undefined, {
		month: 'short',
		day: 'numeric',
		hour: '2-digit',
		minute: '2-digit'
	});
}

export function formatRelative(value?: string | number | Date | { seconds?: bigint | number; nanos?: number }) {
	if (!value) return '—';
	let date: Date;
	if (typeof value === 'object' && value !== null && 'seconds' in value && !(value instanceof Date)) {
		date = new Date(Number(value.seconds) * 1000);
	} else if (typeof value === 'string' || typeof value === 'number') {
		date = new Date(value);
	} else {
		date = value as Date;
	}
	const diffMs = Date.now() - date.getTime();
	const minutes = Math.round(diffMs / 60000);
	if (minutes < 1) return 'just now';
	if (minutes < 60) return `${minutes}m ago`;
	const hours = Math.round(minutes / 60);
	if (hours < 24) return `${hours}h ago`;
	const days = Math.round(hours / 24);
	return `${days}d ago`;
}

export function formatScore(score?: number | null, digits = 2) {
	if (score === undefined || score === null || Number.isNaN(score)) {
		return '—';
	}
	return score.toFixed(digits);
}

const statusColorMap: Record<Status, string> = {
	[Status.UNSPECIFIED]: '#757575',
	[Status.AWAITING_START]: '#0066CC',
	[Status.RUNNING]: '#F57C00',
	[Status.DONE]: '#2D7D32',
	[Status.ERROR]: '#C62828'
};

const statusLabelMap: Record<Status, string> = {
	[Status.UNSPECIFIED]: 'Unspecified',
	[Status.AWAITING_START]: 'Queued',
	[Status.RUNNING]: 'Running',
	[Status.DONE]: 'Completed',
	[Status.ERROR]: 'Error'
};

export function getStatusColor(status: Status) {
	return statusColorMap[status] ?? 'var(--gray-5)';
}

export function getStatusLabel(status: Status) {
	return statusLabelMap[status] ?? status;
}

