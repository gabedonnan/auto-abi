import json
import eth_abi


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

    def _generate_from_function(self, func: dict) -> list[str]:
        func_name = func["name"]
        inp_names = []
        inp_types = []
        for inp in func["inputs"]:
            inp_name, inp_type = self._type_mapper(inp)
            inp_names.append(inp_name)
            inp_types.append(inp_type)

        out_types = [out["type"] for out in func["outputs"]]

        param_string = self._generate_param_string(inp_names, inp_types)
        output_types = self._generate_output_types(out_types)
        return [f"   def {func_name}({param_string}) -> {output_types}:",
                f"       "]

    @staticmethod
    def _generate_param_string(inp_names: list[str], inp_types: list[str]) -> str:
        return ", ".join([f"{inp_name}: {inp_type}" for inp_name, inp_type in zip(inp_names, inp_types)])

    @staticmethod
    def _generate_output_types(out_types: list[str]) -> str:
        return " | ".join(out_types)

    def _generate_preamble(self) -> list[str]:
        return [
            "import eth_abi",
            f"class {self.abi_name}:",
        ]

    def _type_mapper(self, inp: dict) -> tuple[str, str]:
        base_type: str
        if "int" in inp["internalType"]:
            base_type = "int"
        elif inp["internalType"] == "bool":
            base_type = "bool"
        elif "address" in inp["internalType"]:
            base_type = "str"
        elif "bytes" in inp["internalType"]:
            base_type = "bytes"
            # TODO CONTINUE #
        else:
            base_type = ""

        return (inp["name"], base_type)