"""Hand-written notes on where specific threads are met in practice.

Only well-established uses are listed. Threads without an entry get no usage note;
a generic list would add nothing.
"""

USES = {
    'M2×0.4': 'M2 screws hold laptop storage drives and small electronics assemblies together.',
    'M2.5×0.45': 'M2.5 is the usual standoff thread for single-board computers and laptop internals.',
    'M3×0.5': 'M3 is the common screw for PC fans, optical and 2.5 inch drives, 3D printer frames '
              'and small enclosures.',
    'M4×0.7': 'M4 is widely used for equipment panels, VESA 75 and VESA 100 monitor mounts and '
              'DIN rail hardware.',
    'M5×0.8': 'M5 is the bicycle accessory thread (bottle cages, racks, mudguards) and a common '
              'size for 19 inch rack screws and aluminium T-slot profiles.',
    'M6×1': 'M6 is the standard cage-nut thread for 19 inch racks in Europe and is used throughout '
            'automotive trim, machine guards and furniture fittings.',
    'M8×1.25': 'M8 is a general machine-building size: engine ancillaries, brackets, mounts for '
               'large displays and T-slot framing.',
    'M10×1.5': 'M10 is used for machine frames, vehicle suspension brackets and light structural work.',
    'M10×1': 'M10×1 is the usual thread for metric brake pipe unions and bleed screws, and for '
             'lamp and sensor fittings.',
    'M10×1.25': 'M10×1.25 is common on Japanese and other Asian vehicles for chassis and engine bolts, '
                'and on some brake fittings.',
    'M12×1.75': 'M12 is used for structural brackets, machine feet and anchor bolts.',
    'M12×1.25': 'M12×1.25 is a wheel stud thread on many Japanese cars and the thread of small '
                'motorcycle spark plugs.',
    'M12×1.5': 'M12×1.5 is one of the most common passenger car wheel stud and wheel bolt threads.',
    'M14×1.25': 'M14×1.25 is the long-standing spark plug thread, which is the only use ISO 261 '
                'lists it for.',
    'M14×1.5': 'M14×1.5 is used for wheel bolts and studs on many European cars and light trucks, '
               'and for oil drain plugs.',
    'M16×1.5': 'M16×1.5 is a common hydraulic port and cable gland thread.',
    'M16×2': 'M16 is a standard structural bolt size in steelwork and heavy machine frames.',
    'M18×1.5': 'M18×1.5 is used for oxygen (lambda) sensors and for larger spark plugs.',
    'M20×1.5': 'M20×1.5 is the most widely used metric cable gland and conduit entry thread.',
    'M20×2.5': 'M20 is a standard structural bolt size for steel connections.',
    'M24×3': 'M24 is a standard structural and anchor bolt size.',
    '#4-40 UNC': '#4-40 is the jack-screw thread on D-sub connectors and a common small '
                 'electronics screw in North America.',
    '#6-32 UNC': '#6-32 holds PC cases, power supplies and 3.5 inch drives, and fastens switches and '
                 'receptacles to North American electrical boxes.',
    '#8-32 UNC': '#8-32 is used for North American electrical box covers, light fixtures and '
                 'machine guards.',
    '#10-24 UNC': '#10-24 is a general-purpose machine screw size in North American equipment.',
    '#10-32 UNF': '#10-32 is the traditional 19 inch rack screw, the green grounding screw in '
                  'electrical boxes and a standard thread for small pneumatic fittings.',
    '1/4-20 UNC': '1/4-20 is the tripod socket thread on cameras (ISO 1222) and the most common '
                  'general-purpose bolt size in North America.',
    '1/4-28 UNF': '1/4-28 is used for grease fittings and small aircraft and automotive fasteners.',
    '5/16-18 UNC': '5/16-18 is a common size for small engine, bracket and furniture bolts.',
    '5/16-24 UNF': '5/16-24 is used on automotive and aircraft fasteners where a fine thread is wanted.',
    '3/8-16 UNC': '3/8-16 is the larger tripod and lighting stand thread (ISO 1222) and a very '
                  'common general-purpose bolt.',
    '3/8-24 UNF': '3/8-24 is used for inverted-flare brake line fittings and automotive fasteners.',
    '7/16-20 UNF': '7/16-20 is a wheel stud thread on older and smaller American cars and the '
                   'straight thread of the SAE -4 O-ring port.',
    '1/2-13 UNC': '1/2-13 is a standard size for structural, machinery and anchor bolts.',
    '1/2-20 UNF': '1/2-20 is a common wheel stud thread on American cars and light trucks and the '
                  'thread of one-piece-crank bicycle pedals.',
    '9/16-18 UNF': '9/16-18 is the pedal thread on adult bicycles (left pedal left-handed) and the '
                   'straight thread of the SAE -6 O-ring port.',
    '5/8-11 UNC': '5/8-11 is the spindle thread on most angle grinders sold in North America and a '
                  'standard structural bolt size.',
    '3/4-10 UNC': '3/4-10 is a standard structural bolt size in steel construction.',
    '3/4-16 UNF': '3/4-16 is the thread of the common spin-on oil filter and of the SAE -8 O-ring port.',
    '1/8 NPT': '1/8 NPT is used for pressure gauges, sensors and grease fittings.',
    '1/4 NPT': '1/4 NPT is the usual thread on air compressor fittings, regulators and pressure gauges.',
    '3/8 NPT': '3/8 NPT is used for air lines, fuel fittings and small hydraulic connections.',
    '1/2 NPT': '1/2 NPT is the common thread for shower arms, domestic water fittings, conduit hubs '
               'and process instruments.',
    '3/4 NPT': '3/4 NPT is used for water heater connections and domestic supply lines.',
    'G1/8': 'G1/8 is used for pneumatic fittings and small pressure gauges.',
    'G1/4': 'G1/4 is the usual thread for pneumatic fittings, pressure gauges and PC water-cooling parts.',
    'G3/8': 'G3/8 is the thread on angle valves and flexible tap connectors in European plumbing.',
    'G1/2': 'G1/2 is the standard thread for taps, shower hoses and radiator valves in Europe.',
    'G3/4': 'G3/4 is the washing machine and dishwasher inlet hose thread and the usual garden tap '
            'thread in Europe.',
    'G1': 'G1 is used for garden taps, pump unions and water meters.',
}
