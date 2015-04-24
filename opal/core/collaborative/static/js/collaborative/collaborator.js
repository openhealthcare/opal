function collaborator($scope) {
    console.log('BROADCST_ENDPOINT');
    console.log(settings.BROADCAST_ENDPONT);
    var socket = new Phoenix.Socket(settings.BROADCAST_ENDPONT);
    socket.connect();
    socket.join("broadcast:elcid", {}).receive("ok", function(chan){
        console.log("Joined a channel !")
        chan.on("change", function(payload){
            console.log('got a change');
            console.log(payload)
            $scope.$broadcast('change', payload)
        });
    })
}
