from graphviz import Digraph

dot = Digraph(comment='The Round Table')

dot.node('A', 'King Arthur')
dot.node('B', 'Sir Bedevere the Wise')
dot.node('L', 'Sir Lancelot the Brave')

# dot.edges([('A', 'B'), ('A', 'L')])

dot.edge('A', 'B', 'AtoB')
dot.edge('A', 'L', 'AtoL')

# 生成GraphViz语法文件,并调用GraphViz打开以绘图
dot.render('graphviz.gv', view=True, format='png')
