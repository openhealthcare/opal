//
// OPAL Flavoured Markdown:
//
// * Linebreakz
//

(function(context, namespace){

    var paragraph = _.template('<p><%= content %></p>');
    var spacey = _.template('<%= content %>  \n');

    var OpalDown = context[namespace] = function(converter){
        return [
            {
                type: 'lang',
                regex: '(.*?)[\n\r]',
                replace: function(match, line){
                    var cleanline = line.trim()
                    if(cleanline){
                        var spaced = spacey({content: cleanline});
                        return spaced
                    }
                    return ""
                }
            }
        ]
    }

})(this.window||exports, 'OpalDown')
