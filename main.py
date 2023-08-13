import re


def read_my_file(file):
    with open(file) as my_Obj:
        my_content = my_Obj.readlines()
        list_of_my_content = []
        for i in my_content:
            list_of_my_content.append(i.strip())
        return list_of_my_content


def all_operation(my_list):
    operation_list = []
    for i in my_list:
        operation_list.append("".join(re.findall('[A-Z]', i)))
    return operation_list


def all_signals(my_list):
    my_all_signals = []
    for i in my_list:
        my_all_signals.append(re.findall('[a-z]', i))
    return my_all_signals


def PI_PO_Diagnosis(my_list):
    my_PI = []
    my_PO = []
    outputs = []
    inputs = []
    for i in my_list:
        outputs.append(i[0])
        inputs.append(i[1:])
    my_temp = []
    for i in range(len(inputs)):
        for j in inputs[i]:
            if j not in outputs and j not in my_PI:
                my_PI.append(j)
            elif j in outputs:
                my_temp.append(j)
    for i in outputs:
        if i not in my_temp and i not in my_PO:
            my_PO.append(i)
    return my_PI, my_PO


def naming_Op(my_op_list):
    op = "op"
    counter = 1
    my_dict = {}
    for i in my_op_list:
        my_dict[op + str(counter)] = i
        counter += 1
    return my_dict


def Quantify_wires(signals, inp):
    my_list = []
    pi, po = PI_PO_Diagnosis(signals)
    one_list_signals = []
    for i in signals:
        for j in i:
            if j not in one_list_signals:
                one_list_signals.append(j)
    if inp:
        for i in one_list_signals:
            if i in pi:
                my_list.append(inp[pi.index(i)])
            else:
                my_list.append('x')
    else:
        for i in one_list_signals:
            if i in pi:
                my_list.append(0)
            else:
                my_list.append('x')
    return one_list_signals, my_list


def named_op_with_pi_po(signals):
    named_op = list(naming_Op(signals).keys())
    op_signals = {}
    for i in range(len(named_op)):
        op_signals[named_op[i]] = signals[i]
    return op_signals


def operation(op, inp1, inp2):
    if op == "AND":
        return int(inp1 and inp2)
    elif op == "OR":
        return int(inp1 or inp2)
    elif op == "NOT":
        return int(not inp1)
    elif op == "NOR":
        return int(not (inp1 or inp2))
    elif op == "XOR":
        return int(((not inp1) and inp2) or ((not inp2) and inp1))


def level(ops, signals):
    name_op = naming_Op(ops)
    my_queue = list(name_op.keys())
    wire_name_list, wires_level = Quantify_wires(signals, 0)
    op_signals = named_op_with_pi_po(signals)
    while my_queue:
        op = my_queue.pop(0)
        gate_inputs = op_signals[op][1:]
        gate_output = op_signals[op][0]
        if len(gate_inputs) > 1:
            inp1_index = wire_name_list.index(gate_inputs[0])
            inp2_index = wire_name_list.index(gate_inputs[1])
            if wires_level[inp1_index] != 'x' and wires_level[inp2_index] != 'x':
                wires_level[wire_name_list.index(gate_output)] = max(wires_level[inp1_index], wires_level[inp2_index]) \
                                                                 + 1
        else:
            inp1_index = wire_name_list.index(gate_inputs[0])
            if wires_level[inp1_index] != 'x':
                wires_level[wire_name_list.index(gate_output)] = wires_level[inp1_index] + 1
    gates_level = {}
    for i in op_signals:
        gates_level[i] = wires_level[wire_name_list.index(op_signals[i][0])]
    gates_level = sorted(gates_level.items(), key=lambda a: a[1])
    return gates_level


# def split_time_value(my_inp):
#     value = {}
#     time = {}
#     for i in my_inp:
#         temp_v = []
#         temp_t = []
#         for j in i:
#             x = re.findall("['v']\d", j)
#             y = re.findall("['@']\d", j)
#             temp_v.append(x[0][1:])
#             temp_t.append(y[0][1:])
#         value[i[0][0]] = temp_v
#         time[i[0][0]] = temp_t
#     return value, time

def the_output(g_level, input_list, signals, op_name):
    pi, po = PI_PO_Diagnosis(signals)
    wire_name_list, wires_value = Quantify_wires(signals, input_list)
    print(wire_name_list)
    op_signals = named_op_with_pi_po(signals)
    print(op_signals)
    for i in g_level:
        op = op_name[i[0]]
        out = op_signals[i[0]][0]
        inp1 = op_signals[i[0]][1]
        if len(op_signals[i[0]]) > 2:
            inp2 = wires_value[wire_name_list.index(op_signals[i[0]][2])]
        else:
            inp2 = 1
        wires_value[wire_name_list.index(out)] = operation(op, wires_value[wire_name_list.index(inp1)], inp2)
    po_out = {}
    for i in po:
        po_out[i] = wires_value[wire_name_list.index(i)]

    return po_out, wires_value


def op_delay(file_as_list):
    all_op = all_operation(file_as_list)
    naming = naming_Op(all_op)
    temp_delay = []
    my_op_delay = {}
    for i in file_as_list:
        temp = re.findall("['#']\d", i)
        temp_delay.append(temp[0][1:])
    counter = 0
    for j in naming:
        my_op_delay[j] = temp_delay[counter]
        counter += 1
    return my_op_delay


def max_path_delay(signals, delay, gates_level):
    op_signals = named_op_with_pi_po(signals)
    time = []
    for i in gates_level:
        t = int(delay[i[0]])
        op_num = i[0]
        out = op_signals[op_num][0]
        counter = 0
        for j in op_signals:
            if out in op_signals[j][1:]:
                out = op_signals[j][0]
                t += int(delay[j])
            counter += 1
        time.append(t)
    return max(time)


def activity_list(event, signals, delay, t):
    op_signals = named_op_with_pi_po(signals)
    act_list = {}
    for i in event:
        for j in op_signals:
            if i in op_signals[j][1:]:
                act_list[op_signals[j][0]] = int(delay[j]) + t
    return act_list


def schedule_event(t, event, act, signals, delay):
    if t == 0:
        return event, activity_list(event, signals, delay, t)
    else:
        temp = []
        my_flag = False
        for i in act:
            if int(act[i]) == t:
                my_flag = True
                temp.append(i)
        if my_flag:
            for i in temp:
                if i in act:
                    act.pop(i)
            t = activity_list(temp, signals, delay, t)
            for j in t:
                act[j] = t[j]
            return temp, act
        else:
            return event, act


def cal_each_gate(event, wire_name, wire_value, op_name, pi, signals):
    temp = {}
    op_signals = named_op_with_pi_po(signals)
    for i in event:
        if i in pi:
            temp[i] = wire_value[wire_name.index(i)]
        else:
            for j in op_signals:
                if i in op_signals[j][0]:
                    if len(op_signals[j]) > 2:
                        inp1 = wire_name.index(op_signals[j][1])
                        inp2 = wire_name.index(op_signals[j][2])
                        value = operation(op_name[j], int(wire_value[inp1]), int(wire_value[inp2]))
                        temp[i] = value
                        wire_value[wire_name.index(i)] = value

                    else:
                        inp1 = wire_name.index(op_signals[j][1])
                        value = operation(op_name[j], int(wire_value[inp1]), 1)
                        temp[i] = value
                        wire_value[wire_name.index(i)] = value
    return wire_value, temp


def unit_delay(events, signals, delays, g_level, inp_list, op_name):
    pi, po = PI_PO_Diagnosis(signals)
    inp_list0 = inp_list.copy()
    inp_list1 = inp_list.copy()
    inp_list1[pi.index(events[0])] = int(events[1])
    wire_name_list, wires_value = Quantify_wires(signals, inp_list1)
    po_output, all_wire_output = the_output(g_level, inp_list0, signals, op_name)
    all_wire_output[wire_name_list.index(events[0])] = int(events[1])
    events = events[0]
    max_delay = max_path_delay(signals, delays, g_level)
    active_list = {}
    e_temp = []
    act_temp = {}
    result = {}

    print(f"time             events          activity_list")
    for t in range(max_delay + 1):
        time = "t"
        time += str(t)
        events, active_list = schedule_event(t, events, active_list, signals, delays)
        if events == e_temp and active_list == act_temp:
            print(f"t={t}")
            result[time] = ' ', ' '
            continue
        e_temp, act_temp = events, active_list
        my_val, x = cal_each_gate(events, wire_name_list, all_wire_output, op_name, pi, signals)
        y = []
        for p in active_list:
            y.append(p)
        result[time] = x, y
        all_wire_output = my_val.copy()
        print(f"t={t}              {x}               {active_list}")
        if not active_list:
            break
    return result


def min_max_delay(events, signals, delays, g_level, min_max_inp_list, op_name):
    my_input = min_max_inp_list
    my_max_input = min_max_inp_list
    my_min_delay = {}
    my_max_delay = {}
    for i in delays:
        my_min_delay[i] = delays[i][0]
        my_max_delay[i] = delays[i][1]
    print(my_min_delay)
    print(my_max_delay)
    min_delay_result = unit_delay(events, signals, my_min_delay, g_level, my_input, op_name)
    max_delay_result = unit_delay(events, signals, my_max_delay, g_level, my_max_input, op_name)
    return min_delay_result,max_delay_result


def show_result(my_delay, o_val):
    my_value = []
    val = o_val
    for i in my_delay:
        temp = my_delay[i][0]
        if primary_output[0] in list(my_delay[i][0]):
            for j in temp:
                if j == primary_output[0]:
                    val = temp[j]
        my_value.append(val)
        print(f"{primary_output[0]}@{i[1:]}V{val}")
    return my_value


get_file_as_list = read_my_file('sample.vh')
my_op = all_operation(get_file_as_list)
my_signals = all_signals(get_file_as_list)
primary_inp, primary_output = PI_PO_Diagnosis(my_signals)
naming_op = naming_Op(my_op)
gate_level = level(my_op, my_signals)
operation_delay = op_delay(get_file_as_list)
print("*" * 100)
inp_list = []
main_input = []
for i in primary_inp:
    inp_list.append(int(input(f"please inter value of {i}: ")))
main_input = inp_list.copy()
po_output, all_wire_output = the_output(gate_level, inp_list, my_signals, naming_op)
print("*" * 100)
print(f"content of list is : {get_file_as_list}")
print(f"operations in file are : {my_op}")
print(f"signals of circuit are: {my_signals}")
print(f"The primary inputs are : {primary_inp}")
print(f"The primary outputs are : {primary_output}")
print(f"Naming all operation and the output is : {naming_op}")
print(f"The operation delays are : {operation_delay}")
print(f"The gates level are : {gate_level}")
print(f"The out put with out delay is :{po_output}")
print("*" * 100)
event = input(f"put the event on one of the inputs[{primary_inp}](write input name and the new value): ")
u_delay = unit_delay(event, my_signals, operation_delay, gate_level, inp_list, naming_op)
print(u_delay)
print("*" * 100)
user_ans = input("Do you want to apply the min_max delay [y/n]: ").lower()
if user_ans.startswith('y'):
    for i in operation_delay:
        min_delay = input(f"Enter the minimum delay of gate {naming_op[i]}: ")
        max_delay = input(f"Enter the maximum delay of gate {naming_op[i]}: ")
        operation_delay[i] = list(min_delay+max_delay)
    min_result, max_result = min_max_delay(event, my_signals, operation_delay, gate_level, main_input, naming_op)
print("*" * 100)
po_val = ""
for p in po_output:
    po_val = po_output[p]
print("unit Delay")
u_v = show_result(u_delay, po_val)
print("*" * 100)
print("Min_Delay")
min_v = show_result(min_result, po_val)
print(min_v)
print("*" * 100)
print("Max_Delay")
max_v = show_result(max_result, po_val)
print(max_v)
print("*" * 100)
print("Min_max Delay")
for j in range(len(max_v) - len(min_v)):
    min_v.append(min_v[-1])
print(f"min_v length is {len(min_v)} and data is : {min_v}")
print(f"max_v length is {len(max_v)} and data is : {max_v}")
min_max_final_result = []
for i in range(len(max_v)):
    if max_v[i] == min_v[i]:
        min_max_final_result.append(max_v[i])
    else:
        min_max_final_result.append("z")
print(f"Min_Max final result is : {min_max_final_result}")
print("*" * 100)

