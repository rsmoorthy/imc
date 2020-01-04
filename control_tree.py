"""
This variable is defining the actions when a particualr button is pressed.
Each seleactable element in the GUI has a uniqe ID which is assigned to it
when a Kivy selectable object is created. All the selectable Elements can be
found in isha_kivy.py

Each of the tree elemts contains of multiple child object which are
lists of dicts. These dicts have the follwing keys:

'func' --> this is a method of the selectable gui object which should be executed
'id' --> defines the id of the gui element which shall be used

The last element of the dict list must always be {'nextid':ID} which defines
the id of the next element which shall be selected. FUnctions are executed
in the list from left to right.

Example:

0:{
    "left": [{'func':'enable', 'id':1},{'nextid':1}],
}

In the above example the behaviour of the gui element with id 0 is defined.
If we selected element with ID=0 and we press the 'left' key the method "enable"
of the object with the ID=1 is executed. Then the nextid is set to one,
meaning that this object will gain keyboard control
"""

selectId = {
    'settings':1,
    'settingsMenu':100,

    'videos':2,
    'vFiles':20000,

    'music':3,
    'mFiles':30000,

    'playlist':4,
    'pFiles':40000,

    'system':0,
    'systemMsg':50000,

    'osd':200,
    'root': 300,

    'powermenu':400,
    'playerCore':500,
    'audioCtrl':600

}

CONTROL_TREE = {
    selectId['system']:{
        "down": [
            {'func':'enable', 'id':selectId['root'], 'args':selectId['videos']},
            {'func':'disable', 'id':selectId['root'], 'args':selectId['system']},
            {'nextid':selectId['videos']}
        ],
        "up":[
            {'func':'disable', 'id':selectId['root'], 'args':selectId['system']},
            {'func':'enable', 'id':selectId['root'], 'args':selectId['settings']},
            {'nextid':selectId['settings']}
        ],
        "right":[
            {
                'func':'enable',
                'id':selectId['systemMsg'],
                'false': [
                    {'func':'disable', 'id':selectId['root'], 'args':selectId['system']},
                    {'nextid':selectId['systemMsg']},
                 ]
            },
        ],
    },
    #
    # Dialog Hnalder on system view
    #
    selectId['systemMsg']:{
        "down":[
            {
                'func':'enable',
                'id':selectId['systemMsg'],
                'true':[
                    {'func':'enable', 'id':selectId['system']},
                    {'nextid':selectId['system']}
                ]
            }

        ],
        "enter":[
            {
                'func':'enter',
                'id':selectId['systemMsg'],
                'true':[
                    {'func':'enable', 'id':selectId['root'], 'args':selectId['system']},
                    {'nextid':selectId['system']},
                ],
            }
        ],
        "left":[{
                'func':'left',
                'id':selectId['systemMsg'],
                'true':[
                    {'func':'disable', 'id':selectId['systemMsg']},
                    {'func':'enable', 'id':selectId['root'], 'args':selectId['system']},
                    {'nextid':selectId['system']}
                ]
        }],
        "right":[{'func':'right', 'id':selectId['systemMsg']}],
        "home":[
                    {'func':'enable', 'id':selectId['root'], 'args':selectId['system']},
                    {'func':'disable', 'id':selectId['systemMsg']},
                    {'nextid':selectId['system']}
                ],
        "back":[
                    {'func':'enable', 'id':selectId['root'], 'args':selectId['system']},
                    {'func':'disable', 'id':selectId['systemMsg']},
                    {'nextid':selectId['system']}
                ],
    },
    #
    # Video control
    #
    selectId['videos']:{
            "right": [
                {'func':'enable', 'id':selectId['vFiles']},
                {'func':'disable', 'id':selectId['root'], 'args':selectId['videos']},
                {'nextid':selectId['vFiles']}
            ],
            "down": [
                {'func':'enable', 'id':selectId['root'], 'args':selectId['music']},
                {'func':'disable', 'id':selectId['root'], 'args':selectId['videos']},
                {'nextid':selectId['music']}
            ],
            "up":[
                {'func':'disable', 'id':selectId['root'], 'args':selectId['videos']},
                {'func':'enable', 'id':selectId['root'], 'args':selectId['system']},
                {'nextid':selectId['system']}
            ],
            "home":[
                {'func':'enable', 'id':selectId['root'], 'args':selectId['system']},
                {'func':'disable', 'id':selectId['root'], 'args':selectId['videos']},
                {'nextid':selectId['system']}
            ],
        },
    #
    #vFile viewer
    #
    selectId['vFiles']:{
        "up":[{'func':'keyUp', 'id':selectId['vFiles']}],
        "down":[{'func':'keyDown', 'id':selectId['vFiles']}],
        "left":[
            {'func':'enable', 'id':selectId['root'], 'args':selectId['videos']},
            {'func':'disable', 'id':selectId['vFiles']},
            {'nextid':selectId['videos']}
        ],
        "enter":[{'func':'keyEnter', 'id':selectId['vFiles']}],
        "back": [
            {
                'func':'keyBack',
                'id':selectId['vFiles'],
                'true':[
                    {'func':'enable', 'id':selectId['root'], 'args':selectId['videos']},
                    {'func':'disable', 'id':selectId['vFiles']},
                    {'nextid':selectId['videos']}
                 ]
            },
            ],
        "home": [
            {'func':'keyHome',
             'id':selectId['vFiles'],
             'true':[
                     {'func':'enable', 'id':selectId['root'], 'args':selectId['system']},
                     {'func':'disable', 'id':selectId['vFiles']},
                     {'nextid':selectId['system']}
                 ]
             }],
     },
     #
     # Music  button
     #
     selectId['music']:{
         "right": [
             {'func':'enable', 'id':selectId['mFiles']},
             {'func':'disable', 'id':selectId['root'], 'args':selectId['music']},
             {'nextid':selectId['mFiles']}
         ],
         "down": [
             {'func':'enable', 'id':selectId['root'], 'args':selectId['playlist']},
             {'func':'disable', 'id':selectId['root'], 'args':selectId['music']},
             {'nextid':selectId['playlist']}
         ],
         "up":[
             {'func':'disable', 'id':selectId['root'], 'args':selectId['music']},
             {'func':'enable', 'id':selectId['root'], 'args':selectId['videos']},
             {'nextid':selectId['videos']}
         ],
         "home":[
             {'func':'enable', 'id':selectId['root'], 'args':selectId['system']},
             {'func':'disable', 'id':selectId['root'], 'args':selectId['music']},
             {'nextid':selectId['system']}
         ],
         "note":"audio menu",
     },
     #
     # Music file viewer
     #
     selectId['mFiles']:{
         "up":[{'func':'keyUp', 'id':selectId['mFiles']}],
         "down":[{'func':'keyDown', 'id':selectId['mFiles']}],
         "left":[
             {'func':'enable', 'id':selectId['root'], 'args':selectId['music']},
             {'func':'disable', 'id':selectId['mFiles']},
             {'nextid':selectId['music']}
         ],
         "enter":[{'func':'keyEnter', 'id':selectId['mFiles']}],
         "back": [
             {
                 'func':'keyBack',
                 'id':selectId['mFiles'],
                 'true':[
                     {'func':'enable', 'id':selectId['root'], 'args':selectId['music']},
                     {'func':'disable', 'id':selectId['mFiles']},
                     {'nextid':selectId['music']}
                  ]
             },
             ],
         "home": [
             {'func':'keyHome',
              'id':selectId['mFiles'],
              'true':[
                      {'func':'enable', 'id':selectId['root'], 'args':selectId['system']},
                      {'func':'disable', 'id':selectId['mFiles']},
                      {'nextid':selectId['system']}
                  ]
          }],
     },
     #
     # Playlist menu button
     #
     selectId['playlist']:{
         "down": [
             {'func':'enable', 'id':selectId['root'], 'args':selectId['settings']},
             {'func':'disable', 'id':selectId['root'], 'args':selectId['playlist']},
             {'nextid':selectId['settings']}
         ],
         "up":[
             {'func':'disable', 'id':selectId['root'], 'args':selectId['playlist']},
             {'func':'enable', 'id':selectId['root'], 'args':selectId['music']},
             {'nextid':selectId['music']}
         ],
         "right":[
             {'func':'disable', 'id':selectId['root'], 'args':selectId['playlist']},
             {'func':'enable', 'id':selectId['pFiles']},
             {'nextid':selectId['pFiles']}
         ],
         "home":[
             {'func':'enable', 'id':selectId['root'], 'args':selectId['system']},
             {'func':'disable', 'id':selectId['root'], 'args':selectId['playlist']},
             {'nextid':selectId['system']}
         ],
         "note":"pFiles",
     },
     #
     # PLaylist file viewer
     #
     selectId['pFiles']:{
        "left":  [{
            'func':'keyLeft',
            'id':selectId['pFiles'],
            'true':[
                {'func':'disable', 'id':selectId['pFiles']},
                 {'func':'enable', 'id':selectId['root'], 'args':selectId['playlist']},
                {'nextid':selectId['playlist']}
            ]
        }],
         "down": [{'func':'keyDown', 'id':selectId['pFiles']}],
         "up":[{
             'func':'keyUp',
             'id':selectId['pFiles'],
             'true':[
                 {'func':'enable', 'id':selectId['playlist']},
                 {'nextid':selectId['playlist']}
             ]
         }],
         "right": [{'func':'keyRight', 'id':selectId['pFiles']}],
         "enter": [{'func':'keyEnter', 'id':selectId['pFiles']}],
         "back": [{'func':'keyBack', 'id':selectId['pFiles']}], #TODO: this is not complete
         "home": [
            {'func':'enable', 'id':selectId['root'], 'args':selectId['system']},
            {'func':'keyHome', 'id':selectId['pFiles']},
            {'nextid':selectId['system']}
        ],
    },
    #
    #Settnigs button
    #
    selectId['settings']:{
        "up": [
            {'func':'enable', 'id':selectId['root'], 'args':selectId['playlist']},
            {'func':'disable', 'id':selectId['root'], 'args':selectId['settings']},
            {'nextid':selectId['playlist']}
        ],
        "down":[
            {'func':'enable', 'id':selectId['root'], 'args':selectId['system']},
            {'func':'disable', 'id':selectId['root'], 'args':selectId['settings']},
            {'nextid':selectId['system']}
        ],
        "right":[
            {'func':'activate', 'id':selectId['settingsMenu']},
            {'func':'disable', 'id':selectId['root'], 'args':selectId['settings']},
            {'nextid':selectId['settingsMenu']}
        ],
        "home":[
            {'func':'enable', 'id':selectId['root'], 'args':selectId['system']},
            {'func':'disable', 'id':selectId['root'], 'args':selectId['settings']},
            {'nextid':selectId['system']}
        ],
    },
    #
    #Settings menu
    #
    selectId['settingsMenu']:{
        "up": [{'func':'disable', 'id':selectId['settingsMenu']}],
        "down":[{'func':'enable', 'id':selectId['settingsMenu']}],
        "left":[{
            'func':'left',
            'id':selectId['settingsMenu'],
            'true':[
                {'func':'enable', 'id':selectId['settings']},
                {'func':'deactivate', 'id':selectId['settingsMenu']},
                {'nextid':selectId['settings']}
             ]
        }],
        "right":[{'func':'right', 'id':selectId['settingsMenu']}],
        "enter":[{'func':'enter', 'id':selectId['settingsMenu']}],
        "home":[
            {'func':'enable', 'id':selectId['root'], 'args':selectId['system']},
            {'func':'deactivate', 'id':selectId['settingsMenu']},
            {'nextid':selectId['system']}
        ],
        "back":[
            {'func':'enable', 'id':selectId['root'], 'args':selectId['settings']},
            {'func':'deactivate', 'id':selectId['settingsMenu']},
            {'nextid':selectId['settings']}
        ],
    },
    #
    # Power off menu control
    #
    selectId['powermenu']:{
        "down": [{'func':'enable', 'id':selectId['powermenu']}],
        "up":[{'func':'disable', 'id':selectId['powermenu']}],
        "enter":[{'func':'enter', 'id':selectId['powermenu']}],
    },
    #
    # OSD controller, passing key presses to OSD application
    #
    selectId['osd']:{
        "left": [{'func':'left', 'id':selectId['osd']}],
        "right":[{'func':'right', 'id':selectId['osd']}],
        "+":[{'func':'volumeUp', 'id':selectId['osd']}],
        "-":[{'func':'volumeDown', 'id':selectId['osd']}],
        "m":[{'func':'mute', 'id':selectId['osd']}],
        "home":[{'func':'disable', 'id':selectId['osd']}],
        "enter":[{'func':'enter', 'id':selectId['osd']}],
        "esc":[{'func':'disable', 'id':selectId['osd']}],
        "back":[{'func':'disable', 'id':selectId['osd']}],
        "up":[{'func':'up', 'id':selectId['osd']}],
        "down":[{'func':'down', 'id':selectId['osd']}],
    },
    #
    # Player Core instance
    #
    selectId['playerCore']:{
        "enter": [{'func':'keyEnter', 'id':selectId['playerCore']}],
    }
}
