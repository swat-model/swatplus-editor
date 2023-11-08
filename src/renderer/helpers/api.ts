import axios from 'axios';

export function useApi() {
	const electron = window.electronApi;
	let globals = electron.getGlobals();
	return axios.create({ baseURL: `http://localhost:${globals.api_port}/` });
}
