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
                    console.log('OpalDown')
                    console.log(match);
                    console.log(line)
                    var cleanline = line.chomp()
                    if(cleanline){
                        var spaced = spacey({content: cleanline});
                        console.log('spaced')
                        console.log(spaced + '!');
                        return spaced
                    }
                    return ""

                }
            }
        ]
    }

})(this.window||exports, 'OpalDown')
