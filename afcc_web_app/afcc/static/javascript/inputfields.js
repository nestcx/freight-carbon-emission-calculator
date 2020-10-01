// This script will be used for manipulating or enforcing limits on input fields of all types


/**
 * Enforce a minimum and maximum number on input fields. 
 * @param {The inputfield calling this function} inputfield 
 */
function enforceMinMaxNumber(inputfield){
  if(inputfield.value != ""){
    // Check if a minimum number value is specified
    if (inputfield.min !== undefined) {
      if(parseInt(inputfield.value) < parseInt(inputfield.min)){
        inputfield.value = inputfield.min;
      }
    }
    // Check if a maximum number value is specified
    if (inputfield.max !== undefined) {
      if(parseInt(inputfield.value) > parseInt(inputfield.max)){
        inputfield.value = inputfield.max;
      }
    }
  }
}