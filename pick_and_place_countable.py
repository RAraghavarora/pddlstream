#!/usr/bin/env python

from __future__ import print_function

from pddlstream.conversion import AND, NOT
from pddlstream.incremental import solve_exhaustive, solve_current, solve_incremental
from pddlstream.focused import solve_focused
from pddlstream.committed import solve_committed

# TODO: each action would be associated with a control primitive anyways
from pddlstream.stream import from_gen_fn, from_fn

DOMAIN_PDDL = """
(define (domain pick-and-place)
  (:requirements :strips :equality)
  (:predicates 
    (Conf ?q)
    (Block ?b)
    (Pose ?p)
    (Kin ?q ?p)
    (AtPose ?p ?q)
    (AtConf ?q)
    (Holding ?b)
    (HandEmpty)
  )
  (:action move
    :parameters (?q1 ?q2)
    :precondition (and (Conf ?q1) (Conf ?q2) 
                       (AtConf ?q1))
    :effect (and (AtConf ?q2)
                 (not (AtConf ?q1))
             (increase (total-cost) 1))
  )
  (:action pick
    :parameters (?b ?p ?q)
    :precondition (and (Block ?b) (Kin ?q ?p)
                       (AtConf ?q) (AtPose ?b ?p) (HandEmpty))
    :effect (and (Holding ?b)
                 (not (AtPose ?b ?p)) (not (HandEmpty)))
  )
  (:action place
    :parameters (?b ?p ?q)
    :precondition (and (Block ?b) (Kin ?q ?p) 
                       (AtConf ?q) (Holding ?b))
    :effect (and (AtPose ?b ?p) (HandEmpty)
                 (not (Holding ?b)))
  )
)
"""

STREAM_PDDL = """
(define (stream pick-and-place)
  (:stream sample-pose
    :inputs ()
    :domain ()
    :outputs (?p)
    :certified (and (Pose ?p))
  )
  (:stream inverse-kinematics
    :inputs (?p)
    :domain (Pose ?p)
    :outputs (?q)
    :certified (and (Conf ?q) (Kin ?q ?p))
  )
)
"""

# TODO: axiom syntax
# TODO: why should you name a function if no use
"""
  (:rule
    :inputs (?q ?p)
    :domain (Pose ?p)
    :outputs (?q)
    :certified (and (Conf ?q) (Kin ?q ?p))
  )
"""

def get_problem1(n_blocks=1, n_poses=5):
    assert(n_blocks + 1 <= n_poses)
    blocks = ['block{}'.format(i) for i in range(n_blocks)]
    #poses = [(x, 0) for x in range(n_blocks)]
    poses = [(x, 0) for x in range(n_blocks+1)]
    #poses = [(x, 0) for x in range(n_poses)]
    conf = (0, 5)
    goal_conf = (5, 5)

    #objects = []
    init = [
        ('Conf', conf),
        ('Conf', goal_conf),
        ('AtConf', conf),
        #('HandEmpty',),
        ('Holding', blocks[0]),

        #(NOT, ('Holding', blocks[0])),  # Confirms that not
        #(EQ, (TOTAL_COST,), 0),
    ]

    init += [('Block', b) for b in blocks]
    init += [('Pose', p) for p in poses]
    init += [('AtPose', b, p) for b, p in zip(blocks, poses)]

    #goal = ('AtConf', conf)
    #goal = ('AtConf', goal_conf)
    #goal = (AND,
    #        ('Holding', blocks[0]),
    #        (NOT, ('HandEmpty',)))
    goal = ('HandEmpty',)
    #goal = (AND,
    #        ('AtPose', blocks[0], poses[1]),
    #        ('AtConf', conf))

    domain_pddl = DOMAIN_PDDL
    stream_pddl = STREAM_PDDL
    stream_map = {
        #'sample-pose': (lambda: (((x, 0),) for x in range(n_blocks, n_poses))),
        'sample-pose': from_gen_fn(lambda: (((x, 0),) for x in range(len(poses), n_poses))),
        #'inverse-kinematics': (lambda p: iter([((p[0], p[1]+1),)])),
        'inverse-kinematics':  from_fn(lambda p: ((p[0], p[1] + 1),)),

    }
    constant_map = {}

    return init, goal, domain_pddl, stream_pddl, stream_map, constant_map

def main():
    problem = get_problem1()
    #plan, cost, init = solve_no_streams(problem)
    #plan, cost, init = solve_exhaustive(problem)
    #plan, cost, init = solve_incremental(problem)
    plan, cost, init = solve_focused(problem, effort_weight=None, verbose=True)
    #plan, cost, init = solve_committed(problem, effort_weight=None, verbose=True)
    print('\n'
          'Cost: {}\n'
          'Plan: {}\n'
          'Init: {}'.format(cost, plan, init))

if __name__ == '__main__':
    main()
