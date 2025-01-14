const URL_REGEX_VALIDATORS = Object.freeze([
  {expression: /[()[\]{};`'"<>]/gmi, expectedTestResult: false},
  {expression: /^([^\w]*)(script|unsafe|javascript|vbscript|app|admin|icloud-sharing|icloud-vetting|help|aim|facetime-audio|applefeedback|ibooks|macappstore|udoc|ts|st|x-apple-helpbasic)/gmi, expectedTestResult: false},
  {expression: /^(?:(?:ht)tps?:|[^a-z]|[a-z+.-]+(?:[^a-z+.\-:]|$))/gmi, expectedTestResult: true},
  {expression: /(javascript:)/gmi, expectedTestResult: false}
]);

const EMPTY_URI = '';

export const sanitizeURI = (uri) => {
  for(let i=0; i < URL_REGEX_VALIDATORS.length; i++){
    if(URL_REGEX_VALIDATORS[i].expression.test(uri) !== URL_REGEX_VALIDATORS[i].expectedTestResult) {
      console.log(`Suspicious URI was detected and deleted: "${uri}"`)
      return EMPTY_URI;
    }
  }

  return uri;
}
