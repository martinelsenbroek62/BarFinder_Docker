import React from 'react';
import PropTypes from 'prop-types';
import Loader from 'react-loader';
import {connect} from 'react-redux';
import {Row, Col, Table} from 'react-bootstrap';

import {usageStatActions} from '../_actions';


class UsageStatPage extends React.Component {

    static propTypes = {
        fetchUsageStat: PropTypes.func.isRequired,
        usageStatFetched: PropTypes.bool.isRequired,
        error: PropTypes.string,
        usageStatInfo: PropTypes.arrayOf(
            PropTypes.shape({
                user_id: PropTypes.number.isRequired,
                user_email: PropTypes.string.isRequired,
                report_time: PropTypes.string.isRequired
            }).isRequired
        ).isRequired
    }

    constructor() {
        super(...arguments);
        const {fetchUsageStat} = this.props;
        fetchUsageStat();
    }

    render() {
        const {usageStatFetched, error, usageStatInfo} = this.props;
        let reportDate;
        if (usageStatInfo && usageStatInfo.length > 0) {
            reportDate = new Date(usageStatInfo[0].report_time);
        } else {
            reportDate = new Date();
        }
        console.warn(error);

        return
    <
        Row >
        < Col >
        < h1 > Usage
        Report < /h1>
        < Loader
        loaded = {usageStatFetched} >
            < p > Reported
        at: {
            reportDate.toLocaleString()
        }
    <
        /p>
        < Table
        striped
        bordered
        hover >
        < thead >
        < tr >
        < th > User
        ID < /th>
        < th > Email < /th>
        < th > Weekly
        Usage < /th>
        < th > Daily
        Usage < /th>
        < /tr>
        < /thead>
        < tbody >
        {
            usageStatInfo.map((user, idx) => (
                < tr key = {idx} >
            < td > {user.user_id} < /td>
            < td > {user.user_email} < /td>
            < td > {user.amount_in_last_week.toLocaleString()}s < /td>
        < td > < ul >
        {
            user.amount_by_day.map(({date, duration}, jdx) => (
                < li key = {jdx} >
            {date}
    :
        {
            duration.toLocaleString()
        }
        s
        < /li>
    ))
    }
    <
        /ul></
        td >
        < /tr>
    ))
    }
    <
        /tbody>
        < /Table>
        < /Loader>
        < /Col>
        < /Row>;

    }

}


function mapState(state) {
    let {usageStatFetched, error, usageStatInfo} = state.usageStat;
    usageStatInfo = usageStatInfo || [];
    return {error, usageStatFetched, usageStatInfo};
}

const actionCreators = {
    fetchUsageStat: usageStatActions.fetch
}

export default connect(mapState, actionCreators)(UsageStatPage);
