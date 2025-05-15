import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  IconButton,
  Typography,
  useMediaQuery,
} from '@mui/material';
import { useTheme as useMuiTheme } from '@mui/material/styles';
import { useTheme } from '../context/ThemeContext';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import DashboardIcon from '@mui/icons-material/Dashboard';
import TimelineIcon from '@mui/icons-material/Timeline';
import AssessmentIcon from '@mui/icons-material/Assessment';
import SettingsIcon from '@mui/icons-material/Settings';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';

const drawerWidth = 240;

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Predictions', icon: <TimelineIcon />, path: '/predictions' },
  { text: 'Model Metrics', icon: <AssessmentIcon />, path: '/metrics' },
  { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
];

const Sidebar = ({ open, onClose }) => {
  const theme = useMuiTheme();
  const { toggleColorMode, mode } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const handleNavigation = (path) => {
    navigate(path);
    if (isMobile) {
      onClose();
    }
  };

  const drawer = (
    <>
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: theme.spacing(0, 1),
          ...theme.mixins.toolbar,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', ml: 2 }}>
          <Typography
            variant="h6"
            noWrap
            component="div"
            sx={{ fontWeight: 600 }}
          >
            Quantis
          </Typography>
        </Box>
        <IconButton onClick={onClose}>
          <ChevronLeftIcon />
        </IconButton>
      </Box>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => handleNavigation(item.path)}
              sx={{
                '&.Mui-selected': {
                  backgroundColor: theme.palette.primary.main + '20',
                  borderRight: `3px solid ${theme.palette.primary.main}`,
                  '&:hover': {
                    backgroundColor: theme.palette.primary.main + '30',
                  },
                },
                '&:hover': {
                  backgroundColor: theme.palette.action.hover,
                },
              }}
            >
              <ListItemIcon
                sx={{
                  color:
                    location.pathname === item.path
                      ? theme.palette.primary.main
                      : 'inherit',
                }}
              >
                {item.icon}
              </ListItemIcon>
              <ListItemText
                primary={item.text}
                sx={{
                  color:
                    location.pathname === item.path
                      ? theme.palette.primary.main
                      : 'inherit',
                }}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <Divider />
      <List>
        <ListItem disablePadding>
          <ListItemButton onClick={toggleColorMode}>
            <ListItemIcon>
              {mode === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
            </ListItemIcon>
            <ListItemText
              primary={mode === 'dark' ? 'Light Mode' : 'Dark Mode'}
            />
          </ListItemButton>
        </ListItem>
      </List>
    </>
  );

  return (
    <Drawer
      variant={isMobile ? 'temporary' : 'persistent'}
      open={open}
      onClose={onClose}
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
        },
      }}
    >
      {drawer}
    </Drawer>
  );
};

export default Sidebar;
