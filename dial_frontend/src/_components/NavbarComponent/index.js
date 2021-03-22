import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';

import Gravatar from 'react-gravatar';
import {
    Navbar, Nav, Dropdown,
    NavItem, NavDropdown
} from 'react-bootstrap';
import NavLink from 'react-bootstrap/NavLink';
import {LinkContainer} from 'react-router-bootstrap';


class NavbarComponent extends React.Component {

    static propTypes = {
        signedIn: PropTypes.bool.isRequired,
        isAdmin: PropTypes.bool.isRequired,
        email: PropTypes.string
    }

    render() {
        const {signedIn, isAdmin, email} = this.props;

        return
    <
        Navbar
        bg = "primary"
        variant = "dark"
        expand = "md" >
            < LinkContainer
        to = "/" >
            < Navbar.Brand > Xcellence < /Navbar.Brand>
            < /LinkContainer>
            < Navbar.Toggle
        aria - controls = "navbar-nav" / >
            < Navbar.Collapse
        id = "navbar-nav" >
            < Nav >
            < LinkContainer
        to = "/" >
            < Nav.Link > Home < /Nav.Link>
            < /LinkContainer>
            < LinkContainer
        to = "/sandbox" >
            < Nav.Link > Sandbox < /Nav.Link>
            < /LinkContainer>
        {
            isAdmin ?
        <
            LinkContainer
            to = "/usage-stat" >
                < Nav.Link > Usage
            Stat < /Nav.Link>
            < /LinkContainer> : null}
            < /Nav>
            < /Navbar.Collapse>
            < Navbar.Collapse
            className = "justify-content-end" >
            < Nav >
            {signedIn ?
            < Dropdown as = {NavItem} >
                < Dropdown.Toggle
            id = "user-nav-dropdown"
            as = {NavLink} >
                < Gravatar
            key = "gravatar"
            className = "md-avatar rounded-circle"
            email = {email}
            size = {24}
            />
            < /Dropdown.Toggle>
            < Dropdown.Menu
            alignRight >
            < LinkContainer
            key = "signout"
            to = "/signout/" >
                < NavDropdown.Item > Sign
            Out < /NavDropdown.Item>
            < /LinkContainer>
            < /Dropdown.Menu>
            < /Dropdown> :
            < LinkContainer
            to = "/signin/" >
                < Nav.Link > Sign
            In < /Nav.Link>
            < /LinkContainer>}
            < /Nav>
            < /Navbar.Collapse>
            < /Navbar>
        }

        }

        function mapState(state) {
            const {signedIn, tokenInfo} = state.auth;
            let email;
            let isAdmin = false;
            if (tokenInfo) {
                email = tokenInfo.email;
                isAdmin = tokenInfo.is_admin;
            }
            return {signedIn, email, isAdmin};
        }

        const ConnectedNavbarComponent = connect(mapState)(NavbarComponent);

        export {ConnectedNavbarComponent as NavbarComponent};
