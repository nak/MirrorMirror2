
var show = function(e){
    //alert("elem " + e + " is \n" + JSON.stringify(e));
    return "JS: " + e + "\n\n" + JSON.stringify(e);
}

/**
 * webkit request fram animator fails with TypeError if a native function object is used, so have to
 * wrap :-(
**/
var nativeFunctionWrapper = function(func, handler){
    var self = this;
    this.funct = function(){
       func();
       handler(webkitRequestAnimationFrame(self.funct));
    }
    this.funct();
}
