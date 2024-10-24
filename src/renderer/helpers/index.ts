import { useApi } from './api';
import { useConstants } from './constants';
import { useErrorHandling } from './errorHandling';
import { useFormatters } from './formatters';
import { useCurrentProject } from '../store/currentProject';
import { useAppUpdate } from '../store/appUpdate';
import { useRunProcess } from './runProcess';
import { useUtilities } from './utilities';

export function useHelpers() {
	const api = useApi();
	const constants = useConstants();
	const errors = useErrorHandling();
	const formatters = useFormatters();
	const currentProject = useCurrentProject();
	const runProcess = useRunProcess();
	const utilities = useUtilities();
	const appUpdate = useAppUpdate();

	return {
		api, constants, errors, formatters, currentProject, runProcess, utilities, appUpdate
	}
}