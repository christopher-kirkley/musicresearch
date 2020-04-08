import React from 'react';

function Projects() {
	fetch('http://127.0.0.1:5000/api/v1.0/project', {
		method: 'get',
	})
		.then((response) => {
			return response.json();
		})
		.then((data) => {
			(data);
		})
	return (
		<div>
		<h1>hey</h1>
		</div>

	);
}

export default Projects
