import React from 'react';
import { LayoutDashboard, Factory, Truck, AlertTriangle, Lightbulb, Zap, Settings, Menu, X, PlayCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const SidebarItem = ({ icon: Icon, label, active, onClick }) => (
    <button
        onClick={onClick}
        className={`flex items-center space-x-3 w-full px-4 py-3 rounded-lg transition-all duration-200 group ${active
            ? 'bg-[#00BAC6]/10 text-[#00BAC6] border-r-2 border-[#00BAC6]'
            : 'text-gray-400 hover:bg-gray-800 hover:text-white'
            }`}
    >
        <Icon size={20} className={active ? 'text-[#00BAC6]' : 'text-gray-500 group-hover:text-white'} />
        <span className="font-medium">{label}</span>
        {active && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-[#00BAC6] shadow-[0_0_8px_rgba(0,186,198,0.8)]" />}
    </button>
);

const Layout = ({ children, onStartTour, isTourRunning }) => {
    const [activeSection, setActiveSection] = React.useState('overview-section');
    const [isMobileMenuOpen, setIsMobileMenuOpen] = React.useState(false);

    const scrollToSection = (id) => {
        const element = document.getElementById(id);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth', block: 'start' });
            setActiveSection(id);
            setIsMobileMenuOpen(false); // Close mobile menu after click
        }
    };

    const SidebarContent = () => (
        <div className="flex flex-col h-full">
            <div className="p-6">
                <div
                    className="flex items-center space-x-2 mb-8 cursor-pointer"
                    onClick={() => scrollToSection('overview-section')}
                >
                    <div className="w-8 h-8 bg-gradient-to-br from-[#00BAC6] to-[#008f99] rounded-lg flex items-center justify-center shadow-lg shadow-[#00BAC6]/20">
                        <span className="font-bold text-white text-lg">L</span>
                    </div>
                    <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
                        LensOS
                    </span>
                </div>

                <nav className="space-y-1">
                    <SidebarItem
                        icon={LayoutDashboard}
                        label="Executive Overview"
                        active={activeSection === 'overview-section'}
                        onClick={() => scrollToSection('overview-section')}
                    />
                    <SidebarItem
                        icon={Factory}
                        label="Production Plan"
                        active={activeSection === 'production-section'}
                        onClick={() => scrollToSection('production-section')}
                    />
                    <SidebarItem
                        icon={Truck}
                        label="Allocation"
                        active={activeSection === 'allocation-section'}
                        onClick={() => scrollToSection('allocation-section')}
                    />
                    <SidebarItem
                        icon={AlertTriangle}
                        label="Risk Monitor"
                        active={activeSection === 'risk-section'}
                        onClick={() => scrollToSection('risk-section')}
                    />
                    <SidebarItem
                        icon={Zap}
                        label="Launch Simulator"
                        active={activeSection === 'simulator-section'}
                        onClick={() => scrollToSection('simulator-section')}
                    />
                </nav>

                {/* Take Tour Button */}
                <div className="mt-8 pt-6 border-t border-slate-100/10">
                    <button
                        onClick={onStartTour}
                        className="flex items-center space-x-3 w-full px-4 py-3 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-[#00BAC6] transition-colors group"
                    >
                        <PlayCircle size={20} className="group-hover:scale-110 transition-transform" />
                        <span className="font-medium">Take Product Tour</span>
                    </button>
                </div>
            </div>

            <div className="mt-auto p-6 border-t border-border">
                <div className="flex items-center space-x-3 p-3 rounded-lg bg-secondary/50 border border-border transform hover:scale-105 transition-transform cursor-pointer group hover:border-[#00BAC6]/50">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-[#FFD700] to-[#FFA500] flex items-center justify-center text-xs font-bold text-black border border-white/10">
                        AC
                    </div>
                    <div>
                        <div className="text-sm font-medium text-foreground">Amit Chaudhary</div>
                        <div className="text-xs text-[#00BAC6] flex items-center">
                            <span className="w-1.5 h-1.5 bg-[#00BAC6] rounded-full mr-1 animate-pulse"></span>
                            online
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );

    return (
        <div className="flex min-h-screen bg-background text-foreground font-sans selection:bg-[#00BAC6]/30">
            {/* Desktop Sidebar (hidden on mobile) */}
            <aside className="hidden lg:flex w-64 border-r border-border bg-card/50 backdrop-blur-xl flex-col fixed h-full z-20">
                <SidebarContent />
            </aside>

            {/* Mobile Header */}
            <div className="lg:hidden fixed top-0 w-full z-30 bg-background/80 backdrop-blur-md border-b border-border px-4 py-3 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 bg-gradient-to-br from-[#00BAC6] to-[#008f99] rounded-lg flex items-center justify-center shadow-lg shadow-[#00BAC6]/20">
                        <span className="font-bold text-white text-lg">L</span>
                    </div>
                    <span className="text-xl font-bold text-slate-900">LensOS</span>
                </div>
                <button
                    onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                    className="p-2 text-slate-600 hover:bg-slate-100 rounded-lg"
                >
                    {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
                </button>
            </div>

            {/* Mobile Navigation Drawer */}
            <AnimatePresence>
                {isMobileMenuOpen && (
                    <>
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="fixed inset-0 bg-black/50 z-40 lg:hidden"
                            onClick={() => setIsMobileMenuOpen(false)}
                        />
                        <motion.aside
                            initial={{ x: '-100%' }}
                            animate={{ x: 0 }}
                            exit={{ x: '-100%' }}
                            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                            className="fixed inset-y-0 left-0 w-64 bg-background border-r border-border z-50 lg:hidden"
                        >
                            <SidebarContent />
                        </motion.aside>
                    </>
                )}
            </AnimatePresence>

            {/* Main Content */}
            <div className={`flex-1 lg:ml-64 relative ${isTourRunning ? '' : 'overflow-hidden'} bg-background pt-16 lg:pt-0`}>
                {/* Background Gradients */}
                <div className="absolute top-0 left-0 w-full h-[500px] bg-gradient-to-b from-[#00BAC6]/5 to-transparent pointer-events-none" />
                <div className="absolute top-[-100px] right-[-100px] w-[500px] h-[500px] bg-[#00BAC6]/10 rounded-full blur-[128px] pointer-events-none" />

                <main className="relative z-0 max-w-7xl mx-auto p-4 md:p-8">
                    {children}
                </main>
            </div>
        </div>
    );
};

export default Layout;
