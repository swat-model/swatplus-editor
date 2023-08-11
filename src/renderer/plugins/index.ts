import { useApi } from './api';
import { useConstants } from './constants';
import { useErrorHandling } from './errorHandling';
import { useFormatters } from './formatters';
import { useProjectStore } from './projectStore';
import { useRunProcess } from './runProcess';
import { useUtilities } from './utilities';

export function usePlugins() {
	const api = useApi();
	const constants = useConstants();
	const errors = useErrorHandling();
	const formatters = useFormatters();
	const currentProject = useProjectStore();
	const runProcess = useRunProcess();
	const utilities = useUtilities();

	return {
		api, constants, errors, formatters, currentProject, runProcess, utilities
	}
}