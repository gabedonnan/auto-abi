import json
import eth_abi


class FunctionBuilder:
    def __init__(
            self,
            func_name: str,
            param_names: list[str],
            param_types: list[str],
            return_types: list[str],
            indentation: int
    ):
        self.func_name = func_name
        self.param_names = param_names
        self.param_types = param_types
        self.indentation = indentation
        self.return_types = return_types

    def gen_string(self) -> str:
        lines = []
        lines.append(
            f"{'   ' * self.indentation}def {self.func_name}({self._param_string()}) -> {self._output_types()}:"
        )
        lines.append(
            f"{'   ' * self.indentation + 1}x = eth_abi.decode({self.param_types}, bytes.fromhex({...})"  # TODO: FIXME
        )

    def _param_string(self) -> str:  # TODO: replace this with python types instead of solidity types
        return ", ".join([f"{inp_name}: {inp_type}" for inp_name, inp_type in zip(self.param_names, self.param_types)])

    def _output_types(self) -> str:
        return " | ".join(self.return_types)


class ABIGenerator:
    """
    Generates a python file at a given directory with ABI encoders and decoders for a given ABI input

    self.abi = list of dicts (decoded from list of JSON objects)

    self.write_filepath = filepath to which the generated file should be output

    self.abi_name = name given to the generated ABI class
    """
    def __init__(self, abi: str, write_filepath: str, abi_name: str = "ABI"):
        self.abi: list[dict] = json.loads(abi)
        self.write_filepath: str = write_filepath
        self.abi_name: str = abi_name

    def make(self) -> None:
        text: list[str] = self._generate_preamble()
        with open(self.write_filepath, "w+") as f:
            for item in self.abi:
                if item["type"] == "function":
                    text.extend(self._generate_from_function(item))

            f.write("\n".join(text))

    def _generate_from_function(self, func: dict) -> FunctionBuilder:
        func_name = func["name"]
        inp_types = [inp["internalType"] for inp in func["inputs"]]
        inp_names = [inp["name"] for inp in func["inputs"]]
        out_types = [out["type"] for out in func["outputs"]]

        return FunctionBuilder(func_name, inp_names, inp_types, out_types, 1)

    def _generate_preamble(self) -> list[str]:
        return [
            "import eth_abi",
            f"class {self.abi_name}:",
        ]