import moment from 'moment';

export function useFormatters() {
	function isNullOrEmpty(value:any, checkNullStr=false) {
		return value === undefined || value === null || value === '' || (checkNullStr && value === 'null');
	}

	function toBoolString(val:any, trueVal = 'Yes', falseVal = 'No', nullVal = '') {
		if (isNullOrEmpty(val)) return nullVal;
		return val ? trueVal : falseVal;
	}

	function toDate(value:any, format = 'llll') {
		if (value) {
			return moment(String(value)).format(format);
		}
	}

	function toDateForForm(value:any) {
		if (isNullOrEmpty(value)) return null;
		return moment(value).format('YYYY-MM-DD');
	}

	function toDateTimeForForm(value:any) {
		if (isNullOrEmpty(value)) return null;
		return moment(value).format('YYYY-MM-DDTHH:mm');
	}

	function toInteger(num:any) {
		return Math.round((num + Number.EPSILON) * 100) / 100;
	}

	function toLower(s:string) {
		if (isNullOrEmpty(s)) return null;
		return s.toLowerCase();
	}

	function toLowerFirstLetter(s:string) {
		return s.charAt(0).toLowerCase() + s.slice(1);
	}

	function toMoneyFormat(value:any) {
		return '$' + toNumberFormat(value, 2);
	}

	function toNumberFormat(value:any, decimals = 1, units = '') {
		return toNumberWithCommas(toRoundNumber(Number(value), decimals)) + units;
	}

	function toNumberWithCommas(x:any) {
		var parts = x.toString().split(".");
		parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
		return parts.join(".");
	}

	function toReadable(text:string) {
		return text.replace(/_/g, ' ');
	}

	function toRoundNumber(num:any, precision:number) {
		let base = 10 ** precision;
		return Number((Math.round(num * base) / base).toFixed(precision));
	}

	function toSum(array:[], prop:string) {
		let total = 0;
		for (let obj of array) {
			total += Number(obj[prop]);
		}
		return total;
	}

	function toUpperFirstLetter(s:string) {
		return s.charAt(0).toUpperCase() + s.slice(1);
	}

	function toValidName(name:any) {
		if (isNullOrEmpty(name)) return name;
		return name.replace(/ /g,"_");
	}

	function toValidFileName(s:any) {
		if (isNullOrEmpty(s)) return s;
		let val = s.replace(/[^A-Za-z0-9_\- ]/g, '');
		val = val.replace(/ /g, '-');
		val = val.replace(/---/g, '-');
		return val.toLowerCase();
	}

	function toValue(value:any, valueIfNull = 'N/A') {
		return isNullOrEmpty(value) ? valueIfNull : value;
	}

	return {
		isNullOrEmpty,
		toBoolString,
		toDate,
		toDateForForm,
		toDateTimeForForm,
		toInteger,
		toLower,
		toLowerFirstLetter,
		toMoneyFormat,
		toNumberFormat,
		toNumberWithCommas,
		toReadable,
		toRoundNumber,
		toSum,
		toUpperFirstLetter,
		toValidName,
		toValidFileName,
		toValue
	}
}
