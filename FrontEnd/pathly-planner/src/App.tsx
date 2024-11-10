import React, { useState, useEffect } from 'react';
import { Container, TextField, Button, Typography, Box, List, ListItemButton, ListItemText, Checkbox, FormControlLabel } from '@mui/material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider } from '@mui/x-date-pickers';

type Task = {
    title: string;
    details: string;
    priority: number;
    dependency: string;
    startTime: Date | null;
    endTime: Date | null;
    location: string;
    movable: boolean;
    deadline: Date | null;
    estimatedTime: string;
    type: 'event' | 'deadline';
};

const App = () => {
    const [tasks, setTasks] = useState<Record<string, Task>>({});
    const [currentTask, setCurrentTask] = useState<Task>({
        title: '',
        details: '',
        priority: 1,
        dependency: '',
        startTime: null,
        endTime: null,
        location: '',
        movable: false,
        deadline: null,
        estimatedTime: '',
        type: 'event'
    });
    const [selectedTask, setSelectedTask] = useState<string | null>(null);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setCurrentTask({ ...currentTask, [name]: value });
    };

    const handleDateChange = (date: Date | null, field: 'startTime' | 'endTime' | 'deadline') => {
        setCurrentTask({ ...currentTask, [field]: date });
    };

    const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setCurrentTask({ ...currentTask, movable: e.target.checked });
    };

    const addTask = () => {
        if (tasks[currentTask.title]) {
            alert("A task with this title already exists. Please choose a unique title.");
            return;
        }

        if (currentTask.type === 'event') {
            if (!currentTask.startTime || !currentTask.endTime) {
                alert("Please specify both start and end times for the event.");
                return;
            }
            if (currentTask.startTime >= currentTask.endTime) {
                alert("The end time must be after the start time for events.");
                return;
            }
        }

        setTasks({ ...tasks, [currentTask.title]: { ...currentTask } });
        setCurrentTask({
            title: '',
            details: '',
            priority: 1,
            dependency: '',
            startTime: null,
            endTime: null,
            location: '',
            movable: false,
            deadline: null,
            estimatedTime: '',
            type: 'event'
        });
    };

    const deleteTask = () => {
        if (selectedTask) {
            const updatedTasks = { ...tasks };
            delete updatedTasks[selectedTask];
            setTasks(updatedTasks);
            setSelectedTask(null);
        }
    };
    
    const submit = async () => {
        console.log("Submitting tasks:", tasks);
        const response = await fetch('http://localhost:5001/tasks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(tasks),
        });
    
        if (response.ok) {
            console.log("Tasks submitted successfully");
        } else {
            console.error("Failed to submit tasks");
        }
    };
    
    const fetchTasks = async () => {
        try {
            const response = await fetch('http://localhost:5001/tasks');
            if (!response.ok) throw new Error(`Error: ${response.status}`);
            const data = await response.json();
            setTasks(data.tasks || {});
        } catch (error) {
            console.error("Error fetching tasks:", error);
            alert("Failed to load tasks. Check console for details.");
        }
    };

    const handleTypeChange = (type: 'event' | 'deadline') => {
        setCurrentTask({ ...currentTask, type });
    };

    useEffect(() => {
        fetchTasks();
    }, []);

    return (
        <LocalizationProvider dateAdapter={AdapterDateFns}>
            <Container maxWidth="md">
                <Box display="flex" justifyContent="space-between" p={2}>
                    {/* Left Column - Input */}
                    <Box flex={1} p={2} border={1} borderRadius={2} bgcolor="#dfe7f0">
                        <Typography variant="h6" gutterBottom>New Task</Typography>
                        <TextField label="Title" name="title" value={currentTask.title} onChange={handleInputChange} fullWidth margin="normal" />
                        <TextField label="Details" name="details" value={currentTask.details} onChange={handleInputChange} fullWidth margin="normal" />
                        <TextField label="Priority (1-10)" name="priority" type="number" value={currentTask.priority} onChange={handleInputChange} fullWidth margin="normal" />
                        <TextField label="Dependency" name="dependency" value={currentTask.dependency} onChange={handleInputChange} fullWidth margin="normal" />

                        <Typography variant="subtitle1">Type</Typography>
                        <Button 
                            variant={currentTask.type === 'event' ? 'contained' : 'outlined'} 
                            onClick={() => handleTypeChange('event')}
                            style={{ marginRight: 8 }}
                        >
                            Event
                        </Button>
                        <Button 
                            variant={currentTask.type === 'deadline' ? 'contained' : 'outlined'} 
                            onClick={() => handleTypeChange('deadline')}
                        >
                            Deadline
                        </Button>

                        {currentTask.type === 'event' ? (
                            <>
                                <DateTimePicker
                                    label="Event Start Time"
                                    value={currentTask.startTime}
                                    onChange={(date) => handleDateChange(date, 'startTime')}
                                    renderInput={(props) => <TextField {...props} fullWidth margin="normal" />}
                                />
                                <DateTimePicker
                                    label="Event End Time"
                                    value={currentTask.endTime}
                                    onChange={(date) => handleDateChange(date, 'endTime')}
                                    renderInput={(props) => <TextField {...props} fullWidth margin="normal" />}
                                />
                                <TextField 
                                    label="Location" 
                                    name="location" 
                                    value={currentTask.location} 
                                    onChange={handleInputChange} 
                                    fullWidth 
                                    margin="normal"
                                />
                                <FormControlLabel
                                    control={
                                        <Checkbox 
                                            checked={currentTask.movable} 
                                            onChange={handleCheckboxChange} 
                                            name="movable" 
                                        />
                                    }
                                    label="Movable"
                                />
                            </>
                        ) : (
                            <>
                                <DateTimePicker
                                    label="Deadline"
                                    value={currentTask.deadline}
                                    onChange={(date) => handleDateChange(date, 'deadline')}
                                    renderInput={(props) => <TextField {...props} fullWidth margin="normal" />}
                                />
                                <TextField 
                                    label="Estimated Time to Complete" 
                                    name="estimatedTime" 
                                    value={currentTask.estimatedTime} 
                                    onChange={handleInputChange} 
                                    fullWidth 
                                    margin="normal"
                                />
                            </>
                        )}

                        <Button variant="contained" color="primary" onClick={addTask} fullWidth>Add Task</Button>
                        <Button variant="outlined" color="secondary" onClick={deleteTask} fullWidth>Delete Task</Button>
                        <Button variant="contained" color="success" onClick={fetchTasks} fullWidth>Submit</Button>
                    </Box>

                    {/* Middle Column - Task Preview */}
                    <Box flex={1} p={2} border={1} borderRadius={2} bgcolor="#b0c4de">
                        <Typography variant="h6" gutterBottom>Task Preview</Typography>
                        <Typography variant="body1"><strong>Title:</strong> {currentTask.title}</Typography>
                        <Typography variant="body1"><strong>Details:</strong> {currentTask.details}</Typography>
                        <Typography variant="body1"><strong>Priority:</strong> {currentTask.priority}</Typography>
                        <Typography variant="body1"><strong>Dependency:</strong> {currentTask.dependency}</Typography>
                        {currentTask.type === 'event' ? (
                            <>
                                <Typography variant="body1"><strong>Start Time:</strong> {currentTask.startTime ? currentTask.startTime.toString() : ''}</Typography>
                                <Typography variant="body1"><strong>End Time:</strong> {currentTask.endTime ? currentTask.endTime.toString() : ''}</Typography>
                                <Typography variant="body1"><strong>Location:</strong> {currentTask.location}</Typography>
                                <Typography variant="body1"><strong>Movable:</strong> {currentTask.movable ? 'Yes' : 'No'}</Typography>
                            </>
                        ) : (
                            <>
                                <Typography variant="body1"><strong>Deadline:</strong> {currentTask.deadline ? currentTask.deadline.toString() : ''}</Typography>
                                <Typography variant="body1"><strong>Estimated Time:</strong> {currentTask.estimatedTime}</Typography>
                            </>
                        )}
                    </Box>

                    {/* Right Column - Task List */}
                    <Box flex={1} p={2} border={1} borderRadius={2} bgcolor="#8faec5">
                        <Typography variant="h6" gutterBottom>Tasks</Typography>
                        <List>
                            {Object.keys(tasks).map((taskTitle) => (
                                <ListItemButton
                                    selected={selectedTask === taskTitle}
                                    onClick={() => setSelectedTask(taskTitle)}
                                    key={taskTitle}
                                >
                                    <ListItemText primary={taskTitle} />
                                </ListItemButton>
                            ))}
                        </List>
                    </Box>
                </Box>
            </Container>
        </LocalizationProvider>
    );
};

export default App;