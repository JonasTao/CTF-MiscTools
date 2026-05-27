"""奇葩编码：Brainfuck / Ook / JSFuck 等（简化实现）"""
import re


class EsotericCodec:
    @staticmethod
    def brainfuck_run(code: str, input_data: str = "") -> str:
        code = re.sub(r"[^+\-<>.,\[\]]", "", code)
        tape = [0] * 30000
        ptr = 0
        out = []
        inp = list(input_data)
        ip = 0
        brackets = {}
        stack = []
        for i, c in enumerate(code):
            if c == "[":
                stack.append(i)
            elif c == "]" and stack:
                j = stack.pop()
                brackets[j] = i
                brackets[i] = j
        steps = 0
        max_steps = 1_000_000
        while ip < len(code) and steps < max_steps:
            c = code[ip]
            if c == ">":
                ptr = (ptr + 1) % 30000
            elif c == "<":
                ptr = (ptr - 1) % 30000
            elif c == "+":
                tape[ptr] = (tape[ptr] + 1) % 256
            elif c == "-":
                tape[ptr] = (tape[ptr] - 1) % 256
            elif c == ".":
                out.append(chr(tape[ptr]))
            elif c == ",":
                tape[ptr] = ord(inp.pop(0)) if inp else 0
            elif c == "[" and tape[ptr] == 0:
                ip = brackets[ip]
            elif c == "]" and tape[ptr] != 0:
                ip = brackets[ip]
            ip += 1
            steps += 1
        return "".join(out)

    @staticmethod
    def ook_to_brainfuck(ook: str) -> str:
        mapping = {
            "Ook. Ook?": ">",
            "Ook? Ook.": "<",
            "Ook. Ook.": "+",
            "Ook! Ook!": "-",
            "Ook! Ook.": ".",
            "Ook. Ook!": ",",
            "Ook! Ook?": "[",
            "Ook? Ook!": "]",
        }
        tokens = re.findall(r"Ook[.!?]\s+Ook[.!?]", ook)
        return "".join(mapping.get(t, "") for t in tokens)

    @staticmethod
    def text_to_brainfuck(s: str) -> str:
        """将文本编码为 Brainfuck（CTF 常见逆向）"""
        result = []
        for ch in s:
            v = ord(ch)
            result.append("+" * v + ".")
            result.append("[-]")
        return "".join(result)

    @staticmethod
    def rot47(s: str) -> str:
        out = []
        for c in s:
            o = ord(c)
            if 33 <= o <= 126:
                out.append(chr(33 + (o - 33 + 47) % 94))
            else:
                out.append(c)
        return "".join(out)
