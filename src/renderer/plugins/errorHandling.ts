export function useErrorHandling() {
	function log(message:any) {
		if (process.env.NODE_ENV === 'development') console.log(message);
	}

	function logError(error:any, defaultMessage:string='') {
		//console.log(error);
		var message = '';

		if (error.response) {
			console.log(error.response);
			console.log(error.response?.data?.stacktrace);
			var r = error.response;
			message = r.data != null && r.data.message != null ? r.data.message : '';
		} else if (error.data) {
			console.log(error.data);
			message = error.data.message != null ? error.data.message : '';
		} else if (error.request) {
			console.log(error.request);
		}

		if (message == '' && defaultMessage == '')
			return null;

		return defaultMessage + ' ' + message;
	}

	return {
		log,
		logError
	}
}
