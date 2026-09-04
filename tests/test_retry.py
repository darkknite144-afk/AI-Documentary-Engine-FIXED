from app.utils.retry import retry_call
def test_retry():
    state={"n":0}
    def fn():
        state["n"]+=1
        if state["n"]<3: raise ValueError("temporary")
        return "ok"
    assert retry_call(fn,3,0)=="ok"
    assert state["n"]==3
