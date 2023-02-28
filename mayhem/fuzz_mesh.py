#! /usr/bin/env python3
from json import JSONDecodeError

import atheris
import sys


import fuzz_helpers

with atheris.instrument_imports(include=["trimesh"]):
    import trimesh
    from trimesh.exchange.load import mesh_loaders

supported_file_types = list(mesh_loaders.keys())

value_err_matchers = ['inhomogeneous', 'dict loader', 'determine']
def TestOneInput(data):
    fdp = fuzz_helpers.EnhancedFuzzedDataProvider(data)
    try:
        if fdp.ConsumeBool():
            # Load from 2D list
            trimesh.Trimesh(
                vertices=fuzz_helpers.build_fuzz_list(fdp, [list, int]),
                faces=fuzz_helpers.build_fuzz_list(fdp, [list, int]))
        else:
            # Load from buffer
            with fdp.ConsumeMemoryFile(all_data=True, as_bytes=False) as f:
                mesh = trimesh.load(f, file_type=fdp.PickValueInList(supported_file_types))
            if fdp.ConsumeBool():
                mesh.split()
            if fdp.ConsumeBool():
                mesh.apply_transform(trimesh.transformations.random_rotation_matrix())
    except JSONDecodeError:
        return -1
    except IndexError as e:
        if 'out of bounds' in str(e):
            return -1
        raise e
    except ValueError as e:
        if any([matcher in str(e) for matcher in value_err_matchers]):
            return -1
        raise e



def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
