from typing import List, Tuple


class DNF:
    """用于LTL公式转NBA的析取范式"""
    # 其中存的是标准型，即alpha合取X(phi)形式的元组(alpha,phi)
    form: List[Tuple[str, str]] = []

    def __init__(self, dnf_: str):
        """传入形如(b∧X(True))∨(a∧X(aUb))的dnf"""
        # 分成若干合取项，形如'(b∧X(True))'
        con_list = dnf_.split('∨')
        # 对每个合取项要分出两部分，形如'b'和'True'
        for con in con_list:
            # 按第一次出现'∧X('的地方分割，得到形如'(a'和'True))'
            alpha, phi = con.split('∧X(', 1)
            # 去掉alpha前的'('和phi后的'))'
            alpha = alpha[1:]  # 形如'a'
            phi = phi[:-2]  # 形如'True'
            self.form.append((alpha, phi))

    def __str__(self):
        ok = ['(' + f[0] + '∧X(' + f[1] + '))' for f in self.form]
        return '∨'.join(ok)
