from graphviz import Digraph

dot = Digraph(comment='The Round Table')

dot.node('A', 'King Arthur')
dot.node('B', 'Sir Bedevere the Wise')
dot.node('L', 'Sir Lancelot the Brave')

dot.edges(['AB', 'AL'])

# 生成GraphViz语法文件,并调用GraphViz打开以绘图
dot.render('graphviz.gv', view=True, format='png')
