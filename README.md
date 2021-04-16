# Install & Build & Start
```bash
git clone https://git.coinse.io/gabin/ifl
cd ifl
git checkout -b expr origin/expr
sh docker_run.sh
```

# In docker
### Test Generation
```bash
cd /root/d4j_expr/shell_scripts
sh generate_test2.sh Lang 1 evosuite 1 180 4001
# sh generate_test2h.sh [project] [bug_version] evosuite [test id] [search budget(s)] [seed]
```

### Iterative FL simulation
```bash
cd /root/d4j_expr
python3.6 main.py Lang 1 -t evosuite -i 1 -b 10
# python3.6 main.py [project] [bug_version] -t evosuite -i [test id] -b [query budget]
```
