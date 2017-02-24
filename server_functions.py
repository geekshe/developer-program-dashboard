############################## Helper Functions ################################

def get_request(sql_filter):

    # Retrieves request objects for a specified environment
    requests = db.session.query(Request).filter(Request.call_code.like(sql_filter)).group_by(Request.aggr_id).all()

    return requests

def get_env_total(sql_filter):

    success_totals = db.session.query(db.func.sum(Request.success_count).label('total')).filter(Request.call_code.like(sql_filter)).group_by(Request.aggr_id).all()

    env_total = Decimal(0)

    for success_total in success_totals:
        env_total += Decimal(success_total.total)

    return env_total

def calc_call_volume(sql_filter):

    sql_filter = sql_filter

    env_requests = get_request(sql_filter)
    env_total = get_env_total(sql_filter)

    env_call_volumes = {}
    for request in env_requests:
        env_call_volumes[request.call_code] = Decimal(request.success_count) / env_total

    return env_call_volumes


def get_weighted_avg_latency(sql_filter):

    sql_filter = sql_filter

    # Get the latency for each call. Returns a list.
    all_latency = db.session.query(Request.avg_response_time).filter(Request.call_code.like(sql_filter)).all()

    # Intitialize the total_latency variable
    total_latency = Decimal(0)

    # Get the volume percent for each call
    # Returns a dictionary
    env_call_volumes = calc_call_volume(sql_filter)

    # Multiply the latency by the volume percent for each call
    # Add those together and divide by the number of calls
    # Return the weighted latency

    weighted_avg_latency = Decimal(0)

    for key in env_call_volumes:
        for latency in all_latency[0]:
            weighted_avg_latency += (env_call_volumes[key] * latency) / Decimal(len(all_latency))

    return weighted_avg_latency

    # avg_latency = total_latency / len(all_latency)

def calc_rating(sql_filter, status_type):

    sql_filter = sql_filter
    status_type = status_type

    return rating


def get_status(status_type):

    status_type = status_type

    if avg_latency < 200:
        status = 'green'
        status_icon = 'fa-check-square'
    elif 200 <= avg_latency < 800:
        status = 'yellow'
        status_icon = 'fa-exclamation'
    elif avg_latency >= 800:
        status = 'red'
        status_icon = 'fa-flash'

    return status, status_icon