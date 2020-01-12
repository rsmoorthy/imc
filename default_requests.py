

imcRequests = {
    "Player": {
        "GetProperties":{
            "jsonrpc": "2.0",
            "method": "Player.GetProperties",
            "params": {
        		"playerid": 1,
        			"properties": ["time", "totaltime"]
            },
            "id": 1
        },
        "PlayPause":{
            "jsonrpc": "2.0",
            "method": "Player.PlayPause",
            "id": 1
        },
        "IsPlaying":{
            "jsonrpc": "2.0",
            "method": "Player.IsPlaying",
            "id": 1
        },
        "IsPaused":{
            "jsonrpc": "2.0",
            "method": "Player.IsPaused",
            "id": 1
        },
        "Play":{
            "jsonrpc": "2.0",
            "method": "Player.Play",
            "id": 1
        },
        "Pause":{
            "jsonrpc": "2.0",
            "method": "Player.Pause",
            "id": 1
        },
        "Stop":{
            "jsonrpc": "2.0",
            "method": "Player.Stop",
            "id": 1
        },
        "Next":{
            "jsonrpc": "2.0",
            "method": "Player.Next",
            "id": 1
        },
        "Previous":{
            "jsonrpc": "2.0",
            "method": "Player.Previous",
            "id": 1
        },
        "Seek":{
            "jsonrpc": "2.0",
            "method": "Player.Seek",
            "params":{
                "start":0
            },
            "id": 1
        },
    },
    "Application":{
        "GetProperties":{
            "jsonrpc": "2.0",
            "method": "Application.GetProperties",
            "params": {
                "properties": ["volume", "muted"]
            },
            "id": 1
        },
    },
    "Input":{
        "next":{
            "jsonrpc": "2.0",
            "method": "Input.next",
            "id": 1
        },
        "previous":{
            "jsonrpc": "2.0",
            "method": "Input.next",
            "id": 1
        }
    },
}
