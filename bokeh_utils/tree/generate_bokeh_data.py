from bokeh_utils.tree.bucheim import tree_layout


def tree_2_json(tree):
    tree_dict = {
        'metadata': {
            'all_attr_list': [],
            'attr_values_dict': {}
        },
        'tree': {
            'attr_name': str(tree.root.data),
            'choices': [],
            'children': []
        }
    }
    tree_2_json_recursive(tree.root, tree_dict['tree'], tree_dict['metadata'])
    tree_dict['metadata']['all_attr_list'].append('Demand')

    return tree_dict


def tree_2_json_recursive(tree_node, dict_node, tree_metadata):
    if tree_node.children:
        for c in tree_node.children:
            node = {
                'attr_name': str(c.data),
                'choices': [(str(ch[0]), str(ch[1])) for ch in c.choices],
                'children': []
            }
            dict_node['children'].append(node)
            tree_2_json_recursive(c, node, tree_metadata)
    else:
        for ch in [(str(ch[0]), str(ch[1])) for ch in tree_node.choices]:
            if not tree_metadata['attr_values_dict'].get(ch[0], None):
                tree_metadata['attr_values_dict'][ch[0]] = []
            if ch[1] not in tree_metadata['attr_values_dict'][ch[0]]:
                tree_metadata['attr_values_dict'][ch[0]].append(ch[1])
            if ch[0] not in tree_metadata['all_attr_list']:
                tree_metadata['all_attr_list'].append(ch[0])


class Node(object):
    ''' Tree node '''
    def __init__(self, parent_name, name, data, children, rem_attr):
        self.parent = parent_name
        self.parentPointer = Node
        self.name = name
        self.data = data
        self.children = children
        self.remainingAttributes = rem_attr
        self.decision = None
        self.value = None
        self.width = 0
        self.coord = (0, 0)
        self.depth = 1

        self.prelim = 0
        self.mod = 0
        self.thread = None
        self.ancestor = self
        self.order_number = 1
        self.change = 0
        self.shift = 0


def get_depth(node, id_index, visited={}):
    if not node.children:
        node.depth = 1
        visited[node] = False
        id_index += 1
        return 1

    max_depth = max([get_depth(child, id_index, visited) for child in node.children])

    node.depth = max_depth + 1
    visited[node] = False
    id_index += 1
    return max_depth + 1


def get_width(node, level):
    ''' Calculate width of the level '''
    if node is None:
        return 0
    if level == 1:
        return 1
    elif level > 1:
        if node.parentPointer:
            node.depth = node.parentPointer.depth - 1
        return sum(get_width(child, level-1) for child in node.children)


def get_max_width(node, depth):
    max_width = 0
    h = depth
    level_widths = []
    for i in range(1, h+1):
        width = get_width(node, i)
        level_widths.append(width)
        if width > max_width:
            max_width = width
    return max_width, level_widths


def generate_node_list(root, visited):
    node_list = []
    queue = [root]
    visited[root] = True

    while queue:

        popped_node = queue.pop(0)
        node_list.append(popped_node)

        for child in popped_node.children:
            if visited[child] is False:
                queue.append(child)
                visited[child] = True

    return node_list


def fill_source(source, node_list):
    ''' Fill the source dictionary to pass bokeh '''
    for node in node_list:
        source["x"].append(node.coord[0])

        source["y"].append(node.coord[1])

        if node.children:
            source["nonLeafNodes_stat"].append('1')
        else:
            source["nonLeafNodes_stat"].append(None)

        source["attribute_type"].append(node.name)
        source["decision"].append(node.decision)
        source["instances"].append(len(node.data))


def generate_bokeh_tree(tree_obj, data_instance):
    data_instance['nodes_map'] = {}
    bokeh_root = Node(parent_name='', name=str(tree_obj.root.data), data=[], children=[], rem_attr=set())

    data_instance['nodes_map'][bokeh_root] = tree_obj.root
    bokeh_root.parentPointer = None
    data_instance['all_attr_list'] = set()
    data_instance['attr_values_dict'] = {}
    dfs(tree_obj.root, bokeh_root, [], data_instance)
    data_instance['all_attr_list'] = list(data_instance['all_attr_list'])
    data_instance['all_attr_list'].append('Demand')
    return bokeh_root


def dfs(tree_node, bokeh_node, path, data_instance):
    if not tree_node.children:
        bokeh_node.decision = str(tree_node.data)
        path.append(bokeh_node.decision)
        bokeh_node.data.append(path)
        bokeh_node.name = 'Demand'
        if not data_instance['attr_values_dict'].get('Demand', None):
            data_instance['attr_values_dict']['Demand'] = set()
        data_instance['attr_values_dict']['Demand'].add(bokeh_node.decision)
    else:
        data_instance['all_attr_list'].add(tree_node.data)

        for c in tree_node.children:
            bokeh_ch = Node(parent_name=str(bokeh_node.name), name=str(c.data), data=[], children=[], rem_attr=set())
            data_instance['nodes_map'][bokeh_ch] = c
            bokeh_ch.parentPointer = bokeh_node
            bokeh_node.children.append(bokeh_ch)
            dfs(c, bokeh_ch, path+[str(c.choices[-1][1])], data_instance)

            attr_value = str(c.choices[-1][0])
            if not data_instance['attr_values_dict'].get(attr_value, None):
                data_instance['attr_values_dict'][attr_value] = set()
            data_instance['attr_values_dict'][attr_value].add(str(c.choices[-1][1]))

            for p in bokeh_ch.data:
                bokeh_node.data.append(p)

            if bokeh_ch.decision is None:
                bokeh_node.remainingAttributes = bokeh_node.remainingAttributes.union(bokeh_ch.remainingAttributes)
                bokeh_node.remainingAttributes.add(bokeh_ch.name)


def get_bokeh_data(tree_obj, data_instance):
    id_index = 0
    root = generate_bokeh_tree(tree_obj, data_instance)
    acc = 1
    visited = {}

    depth = get_depth(root, id_index, visited)
    width, level_width = get_max_width(root, depth)

    source = {"nonLeafNodes_stat": [], "attribute_type": [], "decision": [],
              "instances": [], "x": [], "y": []}

    node_list = generate_node_list(root, visited)

    for node in node_list:
        if node.parentPointer:
            node.order_number = node.parentPointer.children.index(node) + 1

    tree_layout(root)

    min_width = min([node.coord[1] for node in node_list])
    if min_width < 1.0:
        padding = 1.0 - min_width

        for node in node_list:
            node.coord = (node.coord[0], node.coord[1] + padding)

    fill_source(source, node_list)
    width = max([node.coord[1] for node in node_list])

    return source, depth, int(width), level_width, acc, node_list
