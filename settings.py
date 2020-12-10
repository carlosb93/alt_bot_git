all_settings = {
    "foray": {
        "emoji": '🗡',
        "subsetts": {
            "status": {
                "validator": [True, False],
                "default": True
            }, 
            "pledge": {
                "validator": [True, False],
                "default": True
            }
        }    
    }, 
    "report": {
        "emoji": '📜',
        "subsetts": {
            "status": {
                "validator": [True, False],
                "default": True
            }, 
            "send_to": {
                "validator": "int",
                "default": 1209077540
            }
        }    
    },
    "order": {
        "emoji": '⚜️',
        "subsetts": {
            "status": {
                "validator": [True, False],
                "default": True
            }, 
            "target": {
                "validator": "order",
                "default": "/g_def" 
            },
            "default": {
                "validator": "order",
                "default": "/g_def" 
            },
            "source": {
                "validator": ["botniato", "default"],
                "default": "botniato" 
            }
        }    
    },
    "sleep": {
        "emoji": '💤',
        "subsetts": {
            "status": {
                "validator": [True, False],
                "default": False
            }, 
            "third": {
                "validator": [1, 2, 3],
                "default": 1
            }
        }    
    },
    "arena": {
        "emoji": '📯',
        "subsetts": {
            "status": {
                "validator": [True, False],
                "default": True
            }, 
            "min_hp": {
                "validator": "int",
                "default": 650
            }
        }    
    },
    "quest": {
        "emoji": '🗺',
        "subsetts": {
            "status": {
                "validator": [True, False],
                "default": True
            }, 
            "min_hp": {
                "validator": "int",
                "default": 350
            }, 
            "morning": {
                "validator": ["Random", "Swamp", "Forest", "Valley", "Foray", None],
                "default": "Swamp"
            },
            "day": {
                "validator": ["Random", "Swamp", "Forest", "Valley", "Foray", None],
                "default": "Forest"
            },
            "evening": {
                "validator": ["Random", "Swamp", "Forest", "Valley", "Foray", None],
                "default": "Valley"
            },
            "night": {
                "validator": ["Random", "Swamp", "Forest", "Valley", "Foray", None],
                "default": "Random"
            },
            "fire": {
                "validator": [True, False],
                "default": True
            },
        }    
    },
    "my_mobs": {
        "emoji": '👾',
        "subsetts": {
            "status": {
                "validator": [True, False],
                "default": True
            }, 
            "send_to": {
                "validator": "int",
                "default": 1209077540
            }
        }    
    },
    "my_ambush": {
        "emoji": '🐙',
        "subsetts": {
            "status": {
                "validator": [True, False],
                "default": True
            }, 
            "send_to": {
                "validator": "int",
                "default": 1066757737
            }
        }    
    },
    "get_mobs": {
        "emoji": '⚔️👾',
        "subsetts": {
            "status": {
                "validator": [True, False],
                "default": False
            }, 
            "from_group": {
                "validator": "int",
                "default": 1066757737
            }
        }    
    },
    "get_ambush": {
        "emoji": '⚔️🐙',
        "subsetts": {
            "status": {
                "validator": [True, False],
                "default": False
            }, 
            "from_group": {
                "validator": "int",
                "default": 1066757737
            }
        }    
    },
    "auction": {
        "emoji": '🛎',
        "subsetts": {
            "status": {
                "validator": [True, False],
                "default": False
            }, 
            "from_group": {
                "validator": "int",
                "default": 1209424945
            }
        }    
    },
    "my_shop": {
        "emoji": '⚒️',
        "subsetts": {
            "status": {
                "validator": [True, False],
                "default": False
            },
            "intensive": {
                "validator": [True, False],
                "default": False
            }
        } 
    }
}
