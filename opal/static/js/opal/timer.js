//
// Log the user out after n seconds.
//
(function(context, namespace){


    var Timer = context[namespace] = {

        start: function(){
            $(document).idleTimer(context.settings.LOG_OUT_DURATION);
            $( document ).on( "idle.idleTimer", function(){
                $( document ).idleTimer("destroy");
                $('#logout-modal').modal().idleTimer(10000)
                $('#logout-modal').on('idle.idleTimer', function(){
                    window.location.pathname = '/accounts/logout/';
                });
            });
        },

        initialize: function(){
            $(document).ready( function(){
                $('#logout-modal').on('hidden.bs.modal', function(){
                    $('#logout-modal').idleTimer('destroy')
                    Timer.start()
                })
            });
        }

    }

    Timer.initialize();
    Timer.start();

})(this.window||exports, "timer")
