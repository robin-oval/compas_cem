__all__ = ["objective_function_numpy"]

# ------------------------------------------------------------------------------
# Gradient calculation with finite differences
# ------------------------------------------------------------------------------

def objective_function_numpy(x, grad, x_func, grad_func, verbose=False):
    """
    """
    print("*********************************")
    print("In objective function")
    if grad.size > 0:
        grad_func(x, grad)
    # fx
    print("====== Computing Objective ======")
    fx = x_func(x)

    if verbose:
        print("Error: {}".format(fx))

    return fx

# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    pass
