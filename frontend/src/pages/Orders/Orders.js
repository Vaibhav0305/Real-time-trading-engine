import React, { useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Button,
  IconButton,
  useTheme,
  TextField,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  Edit as EditIcon,
  Cancel as CancelIcon,
  Visibility as ViewIcon,
  Add as AddIcon
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';

const StyledCard = styled(Card)(({ theme }) => ({
  height: '100%',
  backgroundColor: theme.palette.background.paper,
  border: `1px solid ${theme.palette.divider}`,
  '&:hover': {
    borderColor: theme.palette.primary.main,
    boxShadow: `0 0 20px rgba(0, 212, 170, 0.1)`,
  },
}));

const Orders = () => {
  const theme = useTheme();
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterSymbol, setFilterSymbol] = useState('all');

  // Mock orders data
  const orders = [
    {
      id: 1,
      order_id: 'ORD-001',
      symbol: 'AAPL',
      side: 'buy',
      order_type: 'limit',
      quantity: 100,
      price: 150.25,
      stop_price: null,
      status: 'pending',
      filled_quantity: 0,
      average_price: null,
      commission: 0,
      created_at: '2024-01-01T10:00:00Z',
      updated_at: '2024-01-01T10:00:00Z',
    },
    {
      id: 2,
      order_id: 'ORD-002',
      symbol: 'GOOGL',
      side: 'sell',
      order_type: 'market',
      quantity: 50,
      price: null,
      stop_price: null,
      status: 'filled',
      filled_quantity: 50,
      average_price: 2800.00,
      commission: 1.50,
      created_at: '2024-01-01T09:30:00Z',
      updated_at: '2024-01-01T09:35:00Z',
    },
    {
      id: 3,
      order_id: 'ORD-003',
      symbol: 'MSFT',
      side: 'buy',
      order_type: 'stop',
      quantity: 75,
      price: 380.50,
      stop_price: 375.00,
      status: 'cancelled',
      filled_quantity: 0,
      average_price: null,
      commission: 0,
      created_at: '2024-01-01T08:00:00Z',
      updated_at: '2024-01-01T08:15:00Z',
    },
    {
      id: 4,
      order_id: 'ORD-004',
      symbol: 'TSLA',
      side: 'sell',
      order_type: 'limit',
      quantity: 25,
      price: 250.00,
      stop_price: null,
      status: 'partial',
      filled_quantity: 15,
      average_price: 250.00,
      commission: 0.75,
      created_at: '2024-01-01T07:00:00Z',
      updated_at: '2024-01-01T07:30:00Z',
    },
  ];

  const symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META'];
  const statuses = ['all', 'pending', 'filled', 'partial', 'cancelled', 'rejected'];

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'warning';
      case 'filled': return 'success';
      case 'partial': return 'info';
      case 'cancelled': return 'error';
      case 'rejected': return 'error';
      default: return 'default';
    }
  };

  const getSideColor = (side) => {
    return side === 'buy' ? 'success' : 'error';
  };

  const filteredOrders = orders.filter(order => {
    if (filterStatus !== 'all' && order.status !== filterStatus) return false;
    if (filterSymbol !== 'all' && order.symbol !== filterSymbol) return false;
    return true;
  });

  const handleEditOrder = (order) => {
    setSelectedOrder(order);
    setEditDialogOpen(true);
  };

  const handleViewOrder = (order) => {
    setSelectedOrder(order);
    setViewDialogOpen(true);
  };

  const handleCancelOrder = (orderId) => {
    // In a real app, this would call the API to cancel the order
    console.log('Cancelling order:', orderId);
  };

  const handleSaveEdit = () => {
    // In a real app, this would call the API to update the order
    console.log('Saving order:', selectedOrder);
    setEditDialogOpen(false);
    setSelectedOrder(null);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <Box sx={{ p: 3, height: '100%', overflow: 'auto' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 700 }}>
          Orders
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          sx={{ backgroundColor: theme.palette.primary.main }}
        >
          New Order
        </Button>
      </Box>

      {/* Filters */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <TextField
            select
            fullWidth
            label="Status"
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            size="small"
          >
            {statuses.map((status) => (
              <MenuItem key={status} value={status}>
                {status === 'all' ? 'All Statuses' : status.charAt(0).toUpperCase() + status.slice(1)}
              </MenuItem>
            ))}
          </TextField>
        </Grid>
        <Grid item xs={12} md={3}>
          <TextField
            select
            fullWidth
            label="Symbol"
            value={filterSymbol}
            onChange={(e) => setFilterSymbol(e.target.value)}
            size="small"
          >
            <MenuItem value="all">All Symbols</MenuItem>
            {symbols.map((symbol) => (
              <MenuItem key={symbol} value={symbol}>
                {symbol}
              </MenuItem>
            ))}
          </TextField>
        </Grid>
      </Grid>

      {/* Orders Table */}
      <StyledCard>
        <CardContent>
          <TableContainer component={Paper} sx={{ backgroundColor: 'transparent' }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Order ID</TableCell>
                  <TableCell>Symbol</TableCell>
                  <TableCell>Side</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell align="right">Quantity</TableCell>
                  <TableCell align="right">Price</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="right">Filled</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredOrders.map((order) => (
                  <TableRow key={order.id} hover>
                    <TableCell>
                      <Typography variant="body2" fontWeight={600}>
                        {order.order_id}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight={600}>
                        {order.symbol}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={order.side.toUpperCase()}
                        size="small"
                        color={getSideColor(order.side)}
                        sx={{ fontSize: '0.75rem' }}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {order.order_type.charAt(0).toUpperCase() + order.order_type.slice(1)}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2">
                        {order.quantity.toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2">
                        {order.price ? `$${order.price.toFixed(2)}` : 'Market'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                        size="small"
                        color={getStatusColor(order.status)}
                        sx={{ fontSize: '0.75rem' }}
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2">
                        {order.filled_quantity.toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {formatDate(order.created_at)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        <IconButton
                          size="small"
                          onClick={() => handleViewOrder(order)}
                          sx={{ color: theme.palette.info.main }}
                        >
                          <ViewIcon fontSize="small" />
                        </IconButton>
                        {order.status === 'pending' && (
                          <>
                            <IconButton
                              size="small"
                              onClick={() => handleEditOrder(order)}
                              sx={{ color: theme.palette.warning.main }}
                            >
                              <EditIcon fontSize="small" />
                            </IconButton>
                            <IconButton
                              size="small"
                              onClick={() => handleCancelOrder(order.id)}
                              sx={{ color: theme.palette.error.main }}
                            >
                              <CancelIcon fontSize="small" />
                            </IconButton>
                          </>
                        )}
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </StyledCard>

      {/* View Order Dialog */}
      <Dialog open={viewDialogOpen} onClose={() => setViewDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Order Details</DialogTitle>
        <DialogContent>
          {selectedOrder && (
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">Order ID</Typography>
                <Typography variant="body1" fontWeight={600}>{selectedOrder.order_id}</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">Symbol</Typography>
                <Typography variant="body1" fontWeight={600}>{selectedOrder.symbol}</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">Side</Typography>
                <Chip
                  label={selectedOrder.side.toUpperCase()}
                  color={getSideColor(selectedOrder.side)}
                  size="small"
                />
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">Type</Typography>
                <Typography variant="body1">{selectedOrder.order_type}</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">Quantity</Typography>
                <Typography variant="body1">{selectedOrder.quantity.toLocaleString()}</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">Price</Typography>
                <Typography variant="body1">
                  {selectedOrder.price ? `$${selectedOrder.price.toFixed(2)}` : 'Market'}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">Status</Typography>
                <Chip
                  label={selectedOrder.status}
                  color={getStatusColor(selectedOrder.status)}
                  size="small"
                />
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">Filled Quantity</Typography>
                <Typography variant="body1">{selectedOrder.filled_quantity.toLocaleString()}</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">Average Price</Typography>
                <Typography variant="body1">
                  {selectedOrder.average_price ? `$${selectedOrder.average_price.toFixed(2)}` : 'N/A'}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">Commission</Typography>
                <Typography variant="body1">${selectedOrder.commission.toFixed(2)}</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">Created</Typography>
                <Typography variant="body1">{formatDate(selectedOrder.created_at)}</Typography>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Edit Order Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Order</DialogTitle>
        <DialogContent>
          {selectedOrder && (
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Quantity"
                  type="number"
                  value={selectedOrder.quantity}
                  onChange={(e) => setSelectedOrder({...selectedOrder, quantity: parseInt(e.target.value)})}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Price"
                  type="number"
                  value={selectedOrder.price || ''}
                  onChange={(e) => setSelectedOrder({...selectedOrder, price: parseFloat(e.target.value)})}
                  helperText="Leave empty for market orders"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Stop Price"
                  type="number"
                  value={selectedOrder.stop_price || ''}
                  onChange={(e) => setSelectedOrder({...selectedOrder, stop_price: parseFloat(e.target.value)})}
                  helperText="Required for stop orders"
                />
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveEdit} variant="contained">Save</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Orders;
