def main(tick, config, q):
    return  # Drafted, TODO


    pc = {
        'id': 1,
        'coords': [0, 0, 0]
    }

    ship = {
        'coords': [0, 0, 0],
        'type': 'freight' or 'settler' or 'corvette' or 'frigate',  # Corvette small tank, Frigate big tank, guns similar
        'storage': {
            'goods': {
            },
            'solids': 0,  # Upkeep for industry
            'metals': 0,  # For structure of skips
            'isotopes': 0,  # For guns of ships
            'ammo': 1000  # For guns to shoot
        }
    }
    pass

if __name__ == "__main__":
    main()