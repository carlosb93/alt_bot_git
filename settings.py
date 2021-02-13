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
            },
            "trader": {
                "validator": [False, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                "default": False
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
            },
            "aiming": {
                "validator": [True, False],
                "default": False
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
    },
    "extra_craft": {
        "emoji": '⚒️💧',
        "subsetts": {
            "status": {
                "validator": [True, False],
                "default": False
            },
            "craft": {
                "validator": ["c_24","c_33", "c_27", "c_28", "c_36"],
                "default": "c_36"
            } 
        } 
    },
    "daily_craft": {
        "emoji": '⚒️',
        "subsetts": {
            "status": {
                "validator": [True, False],
                "default": True
            },
            "craft": {
                "validator": ["c_14","c_19", "c_20", "c_21", "c_22", "c_23", "c_24"],
                "default": "c_19"
            },
            "gold": {
                "validator": "int",
                "default": "20"
            }
        } 
    }
}
