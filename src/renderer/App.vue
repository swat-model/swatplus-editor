<script setup lang="ts">
	import { reactive, ref, onMounted } from 'vue';
	import { useTheme } from 'vuetify';
	const theme = useTheme();
	const electron = window.electronApi;

	let globals = electron.getGlobals();
	electron.setWindowTitle(`SWAT+ Editor ${globals.version}`);
	
	let page:any = reactive({
		errors: false,
		projectPath: globals.project_path,
		colorTheme: 'auto'
	})

	function quitApp():void {
		electron.quitApp();
	}

	function getColorTheme():void {
		let colorTheme = localStorage.getItem('colorTheme');
		setColorTheme(colorTheme);
	}

	function setColorTheme(colorTheme:string|null):void {
		if (colorTheme === null) colorTheme = 'light';
		page.colorTheme = colorTheme;
		theme.global.name.value = colorTheme;
		electron.setColorTheme(colorTheme);
		localStorage.setItem('colorTheme', colorTheme);
	}

	function toggleColorTheme():void {
		if (page.colorTheme === 'light') setColorTheme('dark');
		else setColorTheme('light');
	}

	onMounted(() => getColorTheme());
</script>

<template>
	<div id="app">
		<v-app id="mainContainer">
			<v-navigation-drawer theme="dark" rail permanent>
				<v-list density="compact" nav>
					<v-list-item prepend-icon="fas fa-folder-open" to="/">
						<v-tooltip activator="parent" location="end">Project setup and information</v-tooltip>
					</v-list-item>
					<v-list-item prepend-icon="fas fa-pencil-alt" to="/">
						<v-tooltip activator="parent" location="end">Edit SWAT+ inputs</v-tooltip>
					</v-list-item>
					<v-list-item prepend-icon="fas fa-play" to="/">
						<v-tooltip activator="parent" location="end">Run SWAT+</v-tooltip>
					</v-list-item>
					<v-list-item prepend-icon="fas fa-check" to="/">
						<v-tooltip activator="parent" location="end">SWAT+ Output Check</v-tooltip>
					</v-list-item>
				</v-list>

				<template #append>
					<v-list density="compact" nav>
						<v-list-item prepend-icon="fas fa-circle-question" to="/">
							<v-tooltip activator="parent" location="end">Help</v-tooltip>
						</v-list-item>
						<v-list-item :prepend-icon="page.colorTheme === 'light' ? 'fas fa-sun' : 'fas fa-moon'" @click="toggleColorTheme">
							<v-tooltip activator="parent" location="end">Toggle color theme</v-tooltip>
						</v-list-item>
					</v-list>
				</template>
			</v-navigation-drawer>

			<v-navigation-drawer permanent id="secondary-nav">
				<div class="pa-3">
					<h1 class="text-h6">SWAT+ Editor {{ globals.version }}</h1>
				</div>
			</v-navigation-drawer>

			<v-main>
				<v-bottom-navigation>
					<v-btn value="recent" @click="quitApp">
						<v-icon>fas fa-arrow-right-from-bracket</v-icon> Quit
					</v-btn>
				</v-bottom-navigation>
			</v-main>
		</v-app>
	</div>
</template>
