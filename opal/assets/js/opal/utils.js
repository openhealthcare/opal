// From http://stackoverflow.com/questions/3629183/why-doesnt-indexof-work-on-an-array-ie8
if (!Array.prototype.indexOf) {
	Array.prototype.indexOf = function(elt /*, from*/)
	{
		var len = this.length >>> 0;
		var from = Number(arguments[1]) || 0;
		from = (from < 0)
		? Math.ceil(from)
		: Math.floor(from);
		if (from < 0)
			from += len;

		for (; from < len; from++)
		{
			if (from in this &&
			    this[from] === elt)
				return from;
		}
		return -1;
	};
}

function clone(obj) {
	if (typeof obj == 'object') {
		return $.extend(true, {}, obj);
	} else {
		return obj;
	}
};

function getTodaysDate() {
	var today = new Date();
	var dd = today.getDate();
	var mm = today.getMonth() + 1;
	var yyyy = today.getFullYear();

	dd = (dd < 10) ? '0' + dd : dd;
	mm = (mm < 10) ? '0' + mm : mm;

	return yyyy + '-' + mm + '-' + dd;
}
