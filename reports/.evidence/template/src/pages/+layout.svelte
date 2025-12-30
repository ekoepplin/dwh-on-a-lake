<script>
	import '@evidence-dev/tailwind/fonts.css';
	import '../app.css';
	import { EvidenceDefaultLayout } from '@evidence-dev/core-components';
	export let data;
</script>

<EvidenceDefaultLayout {data} hideSidebar={false} logo='logo.png' neverShowQueries={false}>
	<slot slot="content" />
</EvidenceDefaultLayout>
