import React, { JSX, useRef } from "react";

interface EmailBodyProps {
	html: string;
}

const EmailBody = ({ html }: EmailBodyProps): JSX.Element => {
	const iframeRef = useRef<HTMLIFrameElement>(null);

	const handleLoad = (): void => {
		const iframe = iframeRef.current;
		if (iframe?.contentDocument?.documentElement) {
			iframe.style.height = iframe.contentDocument.documentElement.scrollHeight + "px";
		}
	};

	return (
		<iframe
			ref={iframeRef}
			srcDoc={html}
			sandbox="allow-same-origin"
			referrerPolicy="no-referrer"
			onLoad={handleLoad}
			title="Email content"
			style={{ width: "100%", border: "none", minHeight: "700px", display: "block" }}
		/>
	);
};

export default EmailBody;
