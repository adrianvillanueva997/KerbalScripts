import krpc
import time


def connectKrpc():
    conn = krpc.connect()
    return conn


def getVessel(conn):
    vessel = conn.space_center.active_vessel
    return vessel


def getInfo(conn, vessel):
    flight_info = vessel.flight()
    altitude = conn.add_stream(getattr, flight_info, 'mean_altitude')
    print(altitude())
    return altitude()


def setThrottle(vessel, throttle, angle):
    vessel.auto_pilot.target_pitch_and_heading(throttle, angle)
    vessel.auto_pilot.engage()
    vessel.control.throttle = 1
    time.sleep(1)


def launch(vessel):
    print('launch!')
    vessel.control.activate_next_stage()


def checkFuel(conn, vessel):
    fuel_amount = conn.get_call(vessel.resources.amount, 'SolidFuel')
    expr = conn.krpc.Expression.less_than(
        conn.krpc.Expression.call(fuel_amount),
        conn.krpc.Expression.constant_float(0.1))
    event = conn.krpc.add_event(expr)
    with event.condition:
        event.wait()
    nextStage(vessel, conn)


def nextStage(vessel, conn):
    a = True
    while a == True:
        if (getInfo(conn, vessel) <= 2500):
            print('Next Stage!')
            vessel.control.activate_next_stage()
            a = False


def main():
    conn = connectKrpc()
    vessel = getVessel(conn)
    setThrottle(vessel, 90, 90)
    launch(vessel)
    checkFuel(conn, vessel)


main()
