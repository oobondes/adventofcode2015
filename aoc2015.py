#!/usr/bin/env python3

import bs4, requests, argparse
from pathlib import Path
from getpass import getpass
from re import findall, DOTALL
import json
import pprint
import random
from math import floor
from tqdm import tqdm
from hashlib import md5

# HELPER FUNCTIONS FOR PUZZLES:


def day_1(text):
    floor = 0
    op = {"(": 1, ")": -1}
    for char in text:
        floor += op[char]
    return floor


def day_1_final(text):
    floor = 0
    op = {"(": 1, ")": -1}
    for i, char in enumerate(text, 1):
        floor += op[char]
        if floor < 0:
            return i
    return floor


def day_2(text):
    total = 0
    for line in text.split():
        nums = list(map(int, line.split("x")))
        sides = sorted([nums[0] * nums[1], nums[0] * nums[2], nums[2] * nums[1]])
        total += 2 * sum(sides) + sides[0]
    return total


def day_2_final(text):
    total = 0
    for line in text.split():
        nums = sorted(map(int, line.split("x")))
        sides = sum(nums[:2]) * 2
        total += nums[0] * nums[1] * nums[2] + sides
    return total


def day_3(text):
    point = (0, 0)
    op = {"v": (0, -1), "^": (0, 1), "<": (-1, 0), ">": (1, 0)}
    visited = {point}
    for direction in text:
        x, y = op[direction]
        point = (point[0] + x, point[1] + y)
        visited.add(point)
    return len(visited)


def day_3_final(text):
    point_s = (0, 0)
    point_r = (0, 0)
    op = {"v": (0, -1), "^": (0, 1), "<": (-1, 0), ">": (1, 0)}
    visited = {point_s}
    for i, direction in enumerate(text):
        x, y = op[direction]
        if i % 2 == 0:
            point_s = (point_s[0] + x, point_s[1] + y)
            visited.add(point_s)
        else:
            point_r = (point_r[0] + x, point_r[1] + y)
            visited.add(point_r)
    return len(visited)


def day_4(text):
    i = 0
    while md5(f"{text}{i}".encode()).hexdigest()[:5] != "00000":
        i += 1
    return i


def day_4_final(text):
    i = 0
    while md5(f"{text}{i}".encode()).hexdigest()[:6] != "000000":
        i += 1
    return i


def day_5(text):
    total = 0
    for line in text.split():
        if len(list(filter(lambda x: x in "aeiou", line))) >= 3 and all([x not in line for x in ["ab", "cd", "pq", "xy"]]) and any([line[i] == line[i + 1] for i in range(len(line) - 1)]):
            total += 1
    return total


def day_5_final(text):
    total = 0
    for line in text.split():
        if any([line[i : i + 2] in line[i + 2 :] for i in range(len(line) - 2)]) and any([line[i] == line[i + 2] for i in range(len(line) - 2)]):
            total += 1
    return total


def day_6(text):
    turn_on = "turn on"
    turn_off = "turn off"
    toggle = "toggle"
    lights = list()
    for i in range(1000):
        lights.append([])
        for j in range(1000):
            lights[i].append(False)
    for line in text.split("\n"):
        first, end = line.split(" through ")
        end_x, end_y = end.split(",")
        option = " ".join(first.split()[:-1])
        start_x, start_y = first.split()[-1].split(",")
        end_x, end_y, start_x, start_y = int(end_x), int(end_y), int(start_x), int(start_y)
        print(f"{option} = {line}")
        for x in range(start_x, end_x + 1):
            for y in range(start_y, end_y + 1):
                if option == toggle:
                    lights[x][y] = not lights[x][y]
                if option == turn_off:
                    lights[x][y] = False
                if option == turn_on:
                    lights[x][y] = True

    return sum([sum(arr) for arr in lights])


def day_6_final(text):
    turn_on = "turn on"
    turn_off = "turn off"
    toggle = "toggle"
    lights = list()
    for i in range(1000):
        lights.append([])
        for j in range(1000):
            lights[i].append(False)
    for line in text.split("\n"):
        first, end = line.split(" through ")
        end_x, end_y = end.split(",")
        option = " ".join(first.split()[:-1])
        start_x, start_y = first.split()[-1].split(",")
        end_x, end_y, start_x, start_y = int(end_x), int(end_y), int(start_x), int(start_y)
        print(f"{option} = {line}")
        for x in range(start_x, end_x + 1):
            for y in range(start_y, end_y + 1):
                if option == toggle:
                    lights[x][y] += 2
                if option == turn_off:
                    if lights[x][y]:
                        lights[x][y] -= 1
                if option == turn_on:
                    lights[x][y] += 1

    return sum([sum(arr) for arr in lights])


class circuit:
    letters = dict()

    def __init__(self, name, op, *dependencies):
        self.name = name
        self.op = op.strip()
        if op.isdigit():
            self.value = int(op)
        else:
            self.dependencies = dependencies
        circuit.letters[name] = self

    def get_value(self):
        if not hasattr(self,'value'):
            deps = [circuit.letters[x].get_value() if not x.isdigit() else int(x) for x in self.dependencies]
            if self.op == "OR":
                self.value = deps[0] | deps[1]
            elif self.op == "AND":
                self.value = deps[0] & deps[1]
            elif self.op == "LSHIFT":
                self.value = deps[0] << deps[1]
            elif self.op == "RSHIFT":
                self.value = deps[0] >> deps[1]
            elif self.op == "NOT":
                self.value = (65079+456) -deps[0]
            else:
                self.value = circuit.letters[self.op].get_value()
        return self.value

    def reset():
        for letter in circuit.letters:
            if hasattr(circuit.letters[letter], 'dependencies') and hasattr(circuit.letters[letter], 'value'):
                delattr(circuit.letters[letter],'value')


def day_7(text):
        for line in text.split('\n'):
            if not line: continue
            operation, name = line.split(' -> ')
            operation = operation.strip().split()
            if len(operation) == 3:
                circuit(name,operation[1],operation[0],operation[2])
            else:
                circuit(name,*operation)
        return circuit.letters['a'].get_value()


def day_7_final(text):
        for line in text.split('\n'):
            if not line: continue
            operation, name = line.split(' -> ')
            operation = operation.strip().split()
            if len(operation) == 3:
                circuit(name,operation[1],operation[0],operation[2])
            else:
                circuit(name,*operation)
        b = circuit.letters['a'].get_value()
        circuit.reset()
        circuit.letters['b'].value = b
        return circuit.letters['a'].get_value()


def day_8(text):
    print("day 8 is not implemented yet")


def day_8_final(text):
    print("day 8 final is not implemented yet")


def day_9(text):
    print("day 9 is not implemented yet")


def day_9_final(text):
    print("day 9 final is not implemented yet")


def day_10(text):
    print("day 10 is not implemented yet")


def day_10_final(text):
    print("day 10 final is not implemented yet")


def day_11(text):
    print("day 11 is not implemented yet")


def day_11_final(text):
    print("day 11 final is not implemented yet")


def day_12(text):
    print("day 12 is not implemented yet")


def day_12_final(text):
    print("day 12 final is not implemented yet")


def day_13(text):
    print("day 13 is not implemented yet")


def day_13_final(text):
    print("day 13 final is not implemented yet")


def day_14(text):
    print("day 14 is not implemented yet")


def day_14_final(text):
    print("day 14 final is not implemented yet")


def day_15(text):
    print("day 15 is not implemented yet")


def day_15_final(text):
    print("day 15 final is not implemented yet")


def day_16(text):
    sue = """children: 3
cats: 7
samoyeds: 2
pomeranians: 3
akitas: 0
vizslas: 0
goldfish: 5
trees: 3
cars: 2
perfumes: 1""".split(
        "\n"
    )
    sue = dict(map(lambda x: x.split(":"), sue))
    for line in text.split("\n"):
        if not line:
            continue
        _ = line.split(" ")
        sue_num = _[1][:-1]
        attrbs = " ".join(_[2:])
        attrbs = dict(map(lambda x: x.split(":"), attrbs.split(", ")))
        if all([sue[key] == attrbs[key] for key in attrbs]):
            return sue_num


def day_16_final(text):
    print("day 16 final is not implemented yet")


def day_17(text):
    print("day 17 is not implemented yet")


def day_17_final(text):
    print("day 17 final is not implemented yet")


def day_18(text):
    print("day 18 is not implemented yet")


def day_18_final(text):
    print("day 18 final is not implemented yet")


def day_19(text):
    print("day 19 is not implemented yet")


def day_19_final(text):
    print("day 19 final is not implemented yet")


def day_20(text):
    print("day 20 is not implemented yet")


def day_20_final(text):
    print("day 20 final is not implemented yet")


def day_21(text):
    print("day 21 is not implemented yet")


def day_21_final(text):
    print("day 21 final is not implemented yet")


def day_22(text):
    print("day 22 is not implemented yet")


def day_22_final(text):
    print("day 22 final is not implemented yet")


def day_23(text):
    print("day 23 is not implemented yet")


def day_23_final(text):
    print("day 23 final is not implemented yet")


def day_24(text):
    print("day 24 is not implemented yet")


def day_24_final(text):
    print("day 24 final is not implemented yet")


def day_25(text):
    print("day 25 is not implemented yet")


def day_25_final(text):
    print("day 25 final is not implemented yet")


# REGISTER ALL METHODS IN A DICTIONARY
day_func = {
    "1": day_1,
    "1_final": day_1_final,
    "2": day_2,
    "2_final": day_2_final,
    "3": day_3,
    "3_final": day_3_final,
    "4": day_4,
    "4_final": day_4_final,
    "5": day_5,
    "5_final": day_5_final,
    "6": day_6,
    "6_final": day_6_final,
    "7": day_7,
    "7_final": day_7_final,
    "8": day_8,
    "8_final": day_8_final,
    "9": day_9,
    "9_final": day_9_final,
    "10": day_10,
    "10_final": day_10_final,
    "11": day_11,
    "11_final": day_11_final,
    "12": day_12,
    "12_final": day_12_final,
    "13": day_13,
    "13_final": day_13_final,
    "14": day_14,
    "14_final": day_14_final,
    "15": day_15,
    "15_final": day_15_final,
    "16": day_16,
    "16_final": day_16_final,
    "17": day_17,
    "17_final": day_17_final,
    "18": day_18,
    "18_final": day_18_final,
    "19": day_19,
    "19_final": day_19_final,
    "20": day_20,
    "20_final": day_20_final,
    "21": day_21,
    "21_final": day_21_final,
    "22": day_22,
    "22_final": day_22_final,
    "23": day_23,
    "23_final": day_23_final,
    "24": day_24,
    "24_final": day_24_final,
    "25": day_25,
    "25_final": day_25_final,
}


def main(day_num, username=None, password=None, online=False, submit=False, part_one=False, part_two=False):
    if online:
        headers = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"}

        login_data = {"commit": "Sign in", "utf8": "%E2%9C%93", "login": username if online and username else "", "password": password if online and password else ""}
        url = "https://github.com/session"
        s = requests.Session()
        r = s.get(url, headers=headers)
        soup = bs4.BeautifulSoup(r.content, "html5lib")
        login_data["authenticity_token"] = soup.find("input", attrs={"name": "authenticity_token"})["value"]
        r = s.post(url, data=login_data, headers=headers)

        git = "https://adventofcode.com/auth/github"
        day = "https://adventofcode.com/2015/day/{}/input"
        submit_answer_url = "https://adventofcode.com/2015/day/{}/answer"
        s.get(git)

    puzzle_input = s.get(day.format(day_num)).content.decode().strip("\n") if online else Path(f"day{day_num}.txt").read_text().strip("\n")
    if part_one:
        print(f"day {day_num} part 1:")
        ans = day_func[day_num](puzzle_input)
        print(ans)
        if submit:
            data = {"level": "1", "answer": str(ans)}
            resp = s.post(submit_answer_url.format(day_num), data=data)
            results = b"one gold star" in resp.content
            print("success" if results else "failed")
    if part_two:
        print(f"day {day_num} part 2:")
        ans = day_func[f"{day_num}_final"](puzzle_input)
        print(ans)
        if submit:
            data = {"level": "2", "answer": str(ans)}
            resp = s.post(submit_answer_url.format(day_num), data=data)
            results = b'<span class="day-success">one gold star</span> closer to collecting enough star fruit.' in resp.content
            print("success" if results else "failed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(__file__)
    parser.add_argument("day", nargs="+", help="sets the day to be ran")
    parser.add_argument("-o", "--online", action="store_true", help="this flag causes the script to pull the input from the website. Otherwise, it will use dayX.txt as input.")
    parser.add_argument("-s", "--submit", action="store_true", help="this flag will submit the answer generated to advent of code.")
    parser.add_argument("-1", "--part_one", action="store_true", help="run the first part of the puzzle")
    parser.add_argument("-2", "--part_two", action="store_true", help="run the second part of the puzzle")
    parser.add_argument("-u", "--username", help="Github username")
    parser.add_argument("-p", "--password", help="github password")
    args = parser.parse_args()
    part_one = True if args.part_one == args.part_two else args.part_one
    part_two = args.part_two
    if args.online:
        username = args.username or input("enter username: ")
        password = args.password or getpass()
    else:
        password = None
        username = None
    for day in args.day:
        main(day, online=args.online, submit=args.submit, username=username, password=password, part_one=part_one, part_two=part_two)
