declare module "*.svg" {
	// for importing as a URL (e.g. in <img src="..." />)
	const src: string;
	export default src;
}

declare module "*.svg?react" {
	import * as React from "react";
	const ReactComponent: React.FunctionComponent<React.SVGProps<SVGSVGElement> & { title?: string }>;
	export default ReactComponent;
}

declare module "*.png" {
	const src: string;
	export default src;
}

declare module "*.jpg" {
	const src: string;
	export default src;
}

declare module "*.jpeg" {
	const src: string;
	export default src;
}

declare module "*.gif" {
	const src: string;
	export default src;
}

declare module "*.webp" {
	const src: string;
	export default src;
}

declare module "*.html" {
	const content: string;
	export default content;
}
